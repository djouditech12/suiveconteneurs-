from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ContainerTracking(models.Model):
    _name = 'container.tracking'
    _description = 'Conteneur'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'expected_arrival_date asc, id desc'

    name = fields.Char(
        string='N° de conteneur', required=True, copy=False, tracking=True,
        index=True)
    departure_date = fields.Date(
        string='Date de départ de Chine', required=True, tracking=True,
        default=fields.Date.context_today)
    expected_arrival_date = fields.Date(
        string="Date d'arrivée prévue", required=True, tracking=True)
    actual_arrival_date = fields.Date(
        string="Date d'arrivée réelle", copy=False, tracking=True)
    state = fields.Selection(
        [('in_transit', 'En route'), ('arrived', 'Arrivé')],
        string='Statut', default='in_transit', required=True,
        tracking=True, copy=False, index=True, group_expand='_group_expand_states')
    line_ids = fields.One2many(
        'container.tracking.line', 'container_id', string='Contenu', copy=True)
    qty_bags = fields.Integer(
        string='Total sacs', compute='_compute_quantities', store=True)
    qty_shoes = fields.Integer(
        string='Total chaussures', compute='_compute_quantities', store=True)
    total_qty = fields.Integer(
        string='Quantité totale (pcs)', compute='_compute_quantities',
        store=True, tracking=True)
    transit_days = fields.Integer(
        string='Durée du trajet (jours)', compute='_compute_transit_days')
    days_left = fields.Integer(
        string='Jours restants', compute='_compute_days_left')
    is_late = fields.Boolean(string='En retard', compute='_compute_days_left')
    color = fields.Integer(string='Couleur', compute='_compute_color')
    partner_id = fields.Many2one(
        'res.partner', string='Fournisseur', tracking=True, index=True)
    forwarder_id = fields.Many2one(
        'res.partner', string='Transitaire', tracking=True, index=True)
    port = fields.Char(string='Port', tracking=True)
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one(
        'res.company', string='Société', default=lambda self: self.env.company)

    _name_uniq = models.Constraint(
        'UNIQUE(name, company_id)',
        'Ce numéro de conteneur existe déjà !',
    )

    @api.model
    def _group_expand_states(self, states, domain):
        return [key for key, _label in self._fields['state'].selection]

    @api.depends('line_ids.quantity', 'line_ids.product_type')
    def _compute_quantities(self):
        for rec in self:
            bags = sum(rec.line_ids.filtered(
                lambda l: l.product_type == 'bag').mapped('quantity'))
            shoes = sum(rec.line_ids.filtered(
                lambda l: l.product_type == 'shoes').mapped('quantity'))
            rec.qty_bags = bags
            rec.qty_shoes = shoes
            rec.total_qty = sum(rec.line_ids.mapped('quantity'))

    @api.depends('departure_date', 'expected_arrival_date', 'actual_arrival_date')
    def _compute_transit_days(self):
        for rec in self:
            end = rec.actual_arrival_date or rec.expected_arrival_date
            if rec.departure_date and end:
                rec.transit_days = (end - rec.departure_date).days
            else:
                rec.transit_days = 0

    @api.depends('state', 'expected_arrival_date')
    def _compute_days_left(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state == 'in_transit' and rec.expected_arrival_date:
                rec.days_left = (rec.expected_arrival_date - today).days
                rec.is_late = rec.days_left < 0
            else:
                rec.days_left = 0
                rec.is_late = False

    @api.depends('state', 'is_late')
    def _compute_color(self):
        for rec in self:
            if rec.state == 'arrived':
                rec.color = 10  # vert
            elif rec.is_late:
                rec.color = 1  # rouge
            else:
                rec.color = 4  # bleu

    @api.constrains('departure_date', 'expected_arrival_date')
    def _check_dates(self):
        for rec in self:
            if (rec.departure_date and rec.expected_arrival_date
                    and rec.expected_arrival_date < rec.departure_date):
                raise ValidationError(
                    "La date d'arrivée prévue doit être postérieure à la date de départ.")

    def action_set_arrived(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.write({
                'state': 'arrived',
                'actual_arrival_date': rec.actual_arrival_date or today,
            })

    def action_set_in_transit(self):
        self.write({'state': 'in_transit', 'actual_arrival_date': False})

    def write(self, vals):
        # Cohérence lors du glisser-déposer dans le kanban
        if vals.get('state') == 'arrived' and 'actual_arrival_date' not in vals:
            today = fields.Date.context_today(self)
            for rec in self:
                super(ContainerTracking, rec).write(
                    dict(vals, actual_arrival_date=rec.actual_arrival_date or today))
            return True
        if vals.get('state') == 'in_transit' and 'actual_arrival_date' not in vals:
            vals = dict(vals, actual_arrival_date=False)
        return super().write(vals)


class ContainerTrackingLine(models.Model):
    _name = 'container.tracking.line'
    _description = 'Contenu du conteneur'
    _order = 'id'

    container_id = fields.Many2one(
        'container.tracking', string='Conteneur', required=True,
        ondelete='cascade', index=True)
    product_type = fields.Selection(
        [('bag', 'Sacs'), ('shoes', 'Chaussures')],
        string='Type', required=True, default='bag')
    description = fields.Char(string='Description / Modèle')
    quantity = fields.Integer(string='Quantité (pcs)', required=True, default=1)

    _quantity_positive = models.Constraint(
        'CHECK(quantity >= 0)',
        'La quantité ne peut pas être négative.',
    )
