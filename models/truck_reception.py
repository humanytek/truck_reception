from openerp import api, fields, models
import requests
import json

class TruckReception(models.Model):
    _inherit = ['truck', 'vehicle.reception', 'mail.thread']
    _name = 'truck.reception'

    state = fields.Selection([
        ('analysis', 'Analysis'),
        ('weight_input', 'Weight Input'),
        ('unloading', 'Unloading'),
        ('weight_output', 'Weight Output'),
        ('done', 'Done'),
    ], default='analysis')

    _defaults = {'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'reg_code'), }

    @api.one
    @api.depends('contract_id')
    def _compute_product_id(self):
        product_id = False
        for line in self.contract_id.order_line:
            product_id = line.product_id.id
            break
        self.product_id = product_id

    @api.one
    @api.depends('contract_id', 'clean_kilos')
    def _compute_delivered(self):
        self.delivered = sum(record.clean_kilos for record in self.contract_id.truck_reception_ids) / 1000

    @api.one
    def fun_unload(self):
        self.state = 'weight_output'

    @api.one
    def humidity_update(self):
    	url = 'http://189.220.177.158:49276'
    	response = requests.get(url)
    	json_data = json.loads(response.text)
    	self.humidity_rate = float(json_data['humedad'].strip())
    	self.density = float(json_data['densidad'].strip())
    	self.temperature = float(json_data['temperatura'].strip())

    @api.one
    def weight_update(self):
        url = 'http://189.220.177.158:49277'
        response = requests.get(url)
        json_data = json.loads(response.text)
        self.input_kilos = float(json_data['peso_entrada'])
        self.output_kilos = float(json_data['peso_salida'])
        self.raw_kilos = float(json_data['peso_neto'])

    @api.multi
    def write(self, vals, recursive=None):
        if not recursive:
            if self.state == 'analysis':
                self.write({'state': 'weight_input'}, 'r')
            elif self.state == 'weight_input':
                self.write({'state': 'unloading'}, 'r')
            elif self.state == 'unloading':
                self.write({'state': 'weight_output'}, 'r')
            elif self.state == 'weight_output':
                self.write({'state': 'done'}, 'r')

        res = super(TruckReception, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        vals['state'] = 'weight_input'
        res = super(TruckReception, self).create(vals)
        return res
