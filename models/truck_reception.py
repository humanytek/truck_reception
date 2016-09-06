from openerp import api, fields, models


class TruckReception(models.Model):
    _inherit = ['truck', 'vehicle.reception', 'mail.thread']
    _name = 'truck.reception'
