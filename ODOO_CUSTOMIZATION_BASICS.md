# Odoo Customization Basics - Car Rental Module Guide

This guide explains the fundamental concepts of Odoo module customization using your car rental modules as examples.

---

## 1. MODULE STRUCTURE

Every Odoo module has this basic structure:
```
my_module/
├── __init__.py          # Python package initializer
├── __manifest__.py      # Module metadata and dependencies
├── models/              # Python business logic
│   ├── __init__.py
│   └── my_model.py
├── views/               # XML user interface
│   └── my_view.xml
├── security/            # Access rights
│   └── ir.model.access.csv
└── data/                # Default data
    └── demo_data.xml
```

---

## 2. HOW TO ADD/CHANGE FIELDS

### A. Adding New Fields to Existing Models (Inheritance)

**Example from `fleet_vehicle.py`:**
```python
class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"  # Inherit existing model
    
    # Add new field
    rental_state = fields.Selection(
        [
            ("available", "Available"),
            ("rented", "Rented"),
            ("maintenance", "Under Maintenance"),
        ],
        string="Rental Status",  # Label shown in UI
        default="available",      # Default value
        tracking=True,            # Track changes in chatter
    )
```

**Field Types:**
- `fields.Char()` - Text (short)
- `fields.Text()` - Text (long)
- `fields.Integer()` - Whole numbers
- `fields.Float()` - Decimal numbers
- `fields.Boolean()` - True/False
- `fields.Date()` - Date only
- `fields.Datetime()` - Date and time
- `fields.Selection()` - Dropdown list
- `fields.Many2one()` - Link to one record
- `fields.One2many()` - Link to many records
- `fields.Many2many()` - Link to many records (both ways)

### B. Renaming Fields (Change Label)

You can't rename the technical field name without data migration, but you can change the label:

```python
# Original field
rental_state = fields.Selection(string="Rental Status")

# Change label only
rental_state = fields.Selection(string="Vehicle Status")
```

### C. Related Fields (Get Value from Another Model)

**Example:**
```python
rental_daily_rate = fields.Float(
    string="Daily Rate (QAR)",
    related="rental_category_id.daily_rate",  # Get from related record
    store=True,      # Save in database (faster)
    readonly=True,   # User can't edit
)
```

This means: "Get the `daily_rate` from the `rental_category_id` record"

---

## 3. HOW TO USE VALUES FROM ONE MODEL IN ANOTHER

### Method 1: Many2one Relationship

**Example from `fleet_vehicle.py`:**
```python
class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"
    
    # Link to category
    rental_category_id = fields.Many2one(
        "fleet.vehicle.category",  # Target model
        string="Rental Category",
    )
    
    # Get value from linked record
    rental_daily_rate = fields.Float(
        related="rental_category_id.daily_rate",
        store=True,
    )
```

### Method 2: Computed Fields

**Example:**
```python
rental_count = fields.Integer(
    string="Rental Count",
    compute="_compute_rental_count"  # Call this method
)

def _compute_rental_count(self):
    for record in self:
        # Search in another model
        record.rental_count = self.env["sale.rental.line"].search_count(
            [("vehicle_id", "=", record.id)]
        )
```

### Method 3: Access Related Model Data in Code

```python
# In sale_order.py
def create_rental_order_lines(self):
    for rental in self.rental_line_ids:
        # Access vehicle data
        vehicle_name = rental.vehicle_id.name
        vehicle_plate = rental.vehicle_id.license_plate
        
        # Access category data through vehicle
        daily_rate = rental.vehicle_id.rental_category_id.daily_rate
```

---

## 4. COMPUTED FIELDS (Auto-Calculate)

### Basic Computed Field

**Example from `sale_order.py`:**
```python
days = fields.Integer(compute="_compute_days", store=True)

@api.depends('start_date', 'end_date')  # Recalculate when these change
def _compute_days(self):
    for rec in self:
        if rec.start_date and rec.end_date:
            rec.days = (rec.end_date - rec.start_date).days + 1
        else:
            rec.days = 0
```

### Computed Field with Multiple Dependencies

```python
subtotal = fields.Float(compute="_compute_total", store=True)

@api.depends('days', 'rent_price')  # Depends on 2 fields
def _compute_total(self):
    for rec in self:
        rec.subtotal = rec.days * rec.rent_price
```

---

## 5. RELATIONSHIPS BETWEEN MODELS

### One2many / Many2one (Parent-Child)

**Example from `sale_order.py`:**
```python
# In parent model (sale.order)
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    rental_line_ids = fields.One2many(
        'sale.rental.line',  # Child model
        'order_id',          # Field in child that links back
        string="Vehicle Rental Lines"
    )

# In child model (sale.rental.line)
class SaleRentalLine(models.Model):
    _name = 'sale.rental.line'
    
    order_id = fields.Many2one(
        'sale.order',      # Parent model
        ondelete='cascade' # Delete children when parent deleted
    )
```

**Usage:**
```python
# Access children from parent
for order in sale_orders:
    for rental_line in order.rental_line_ids:
        print(rental_line.vehicle_id.name)

# Access parent from child
for rental_line in rental_lines:
    print(rental_line.order_id.name)
```

---

## 6. SEARCHING AND FILTERING DATA

### Search for Records

```python
# Find all available vehicles
available_vehicles = self.env['fleet.vehicle'].search([
    ('rental_state', '=', 'available')
])

# Count records
count = self.env['sale.rental.line'].search_count([
    ('vehicle_id', '=', record.id)
])

# Search with multiple conditions
vehicles = self.env['fleet.vehicle'].search([
    ('rental_state', '=', 'available'),
    ('rental_category_id', '!=', False),  # Has category
])
```

### Domain Operators
- `=` - equals
- `!=` - not equals
- `>`, `<`, `>=`, `<=` - comparisons
- `in` - in list
- `not in` - not in list
- `like` - contains text
- `ilike` - contains text (case insensitive)

---

## 7. CREATING RECORDS PROGRAMMATICALLY

**Example from `sale_order.py`:**
```python
def create_rental_order_lines(self):
    # Create new record
    self.env['sale.order.line'].create({
        'order_id': self.id,
        'product_id': product.id,
        'name': description,
        'product_uom_qty': rental.days,
        'price_unit': rental.rent_price,
    })
```

---

## 8. MODIFYING VIEWS (XML)

### Inherit Existing View

**Example from `fleet_vehicle_view.xml`:**
```xml
<record id="view_fleet_vehicle_form_inherit" model="ir.ui.view">
    <field name="name">fleet.vehicle.form.inherit</field>
    <field name="model">fleet.vehicle</field>
    <field name="inherit_id" ref="fleet.fleet_vehicle_view_form"/>
    <field name="arch" type="xml">
        
        <!-- Add button after existing buttons -->
        <xpath expr="//div[@name='button_box']" position="inside">
            <button name="action_view_rentals" 
                    type="object" 
                    class="oe_stat_button" 
                    icon="fa-list">
                <field name="rental_count" widget="statinfo" string="Rentals"/>
            </button>
        </xpath>
        
    </field>
</record>
```

### XPath Positions
- `inside` - Add inside element
- `after` - Add after element
- `before` - Add before element
- `replace` - Replace element
- `attributes` - Modify attributes

---

## 9. VALIDATION AND CONSTRAINTS

**Example from `sale_order.py`:**
```python
@api.constrains('start_date', 'end_date')
def _check_dates(self):
    for rec in self:
        if rec.start_date and rec.end_date:
            if rec.end_date < rec.start_date:
                raise ValidationError("End date must be after start date.")
```

---

## 10. PRACTICAL EXAMPLE: Complete Flow

Let's trace how data flows in your car rental system:

### Step 1: Create Vehicle Category
```python
# Model: fleet.vehicle.category
category = {
    'name': 'SUV',
    'daily_rate': 250.0,  # QAR per day
}
```

### Step 2: Assign Category to Vehicle
```python
# Model: fleet.vehicle (inherited)
vehicle = {
    'name': 'Toyota Land Cruiser',
    'license_plate': 'ABC 123',
    'rental_category_id': category.id,  # Link to category
    'rental_state': 'available',
}
# rental_daily_rate automatically gets 250.0 from category
```

### Step 3: Create Rental
```python
# Model: sale.rental.line
rental = {
    'vehicle_id': vehicle.id,  # Link to vehicle
    'start_date': '2024-01-01',
    'end_date': '2024-01-05',
    'rent_price': vehicle.rental_daily_rate,  # Gets 250.0
}
# days automatically computed: 5 days
# subtotal automatically computed: 5 * 250 = 1250
```

### Step 4: Add to Sale Order
```python
# Model: sale.order (inherited)
sale_order = {
    'partner_id': customer.id,
    'rental_line_ids': [(4, rental.id)],  # Link rental
}
# rental_total automatically computed: sum of all rental subtotals
```

---

## 11. COMMON PATTERNS

### Pattern 1: Smart Button (Show Related Records)
```python
# In model
rental_count = fields.Integer(compute="_compute_rental_count")

def _compute_rental_count(self):
    for record in self:
        record.rental_count = self.env["sale.rental.line"].search_count([
            ("vehicle_id", "=", record.id)
        ])

def action_view_rentals(self):
    return {
        'type': 'ir.actions.act_window',
        'name': 'Vehicle Rentals',
        'res_model': 'sale.rental.line',
        'view_mode': 'list,form',
        'domain': [('vehicle_id', '=', self.id)],
    }
```

### Pattern 2: Automatic Discount Calculation
```python
@api.depends("daily_rate")
def _compute_weekly_rate(self):
    for record in self:
        # 7 days with 15% discount
        record.weekly_rate = record.daily_rate * 7 * 0.85
```

### Pattern 3: Override Standard Method
```python
def action_confirm(self):
    # Do custom logic before
    for order in self:
        if order.rental_line_ids:
            order.create_rental_order_lines()
    
    # Call original method
    return super(SaleOrder, self).action_confirm()
```

---

## 12. QUICK REFERENCE

### Access Environment
```python
self.env['model.name']  # Access any model
self.env.user           # Current user
self.env.company        # Current company
self.env.ref('module.xml_id')  # Get record by XML ID
```

### Record Operations
```python
record.write({'field': value})  # Update
record.unlink()                 # Delete
record.copy()                   # Duplicate
record.ensure_one()             # Ensure single record
```

### Field Operations
```python
records.mapped('field_name')    # Get list of field values
records.filtered(lambda r: r.field > 10)  # Filter records
records.sorted(key=lambda r: r.name)      # Sort records
```

---

## NEXT STEPS

1. **Modify existing fields**: Change labels, add help text
2. **Add new fields**: Practice with different field types
3. **Create computed fields**: Auto-calculate values
4. **Link models**: Use Many2one, One2many relationships
5. **Customize views**: Add fields to forms and lists
6. **Add business logic**: Write methods and validations

---

**Remember**: Always test in a development environment first!
