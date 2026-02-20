# Car Rental Qatar & Car Rental Qatar Full – Beginner’s Guide

This guide explains the **structure** of both modules, how **inheritance** works in Odoo, and the **basics** you need to understand the code.

---

## 1. Overview: Two Modules

| Module | Purpose | Depends on |
|--------|---------|------------|
| **car_rental_qatar** | Extends Fleet + **car_rent** with Qatar-specific vehicle fields and rental categories | `base`, `fleet`, **car_rent** |
| **car_rental_qatar_full** | Standalone car rental system: contracts, inspections, documents, dashboard | `base`, `mail`, `fleet`, `sale_management`, `account`, `stock` |

- **car_rental_qatar**: builds on the existing **car_rent** module (rentals = `sale.rental.line`).
- **car_rental_qatar_full**: does **not** depend on car_rent; it has its own **rental.contract** and full rental flow.

---

## 2. Folder Structure

### car_rental_qatar (smaller – extensions only)

```
car_rental_qatar/
├── __init__.py              # Loads the module
├── __manifest__.py          # Module metadata & dependencies
├── models/
│   ├── __init__.py          # Imports: fleet_vehicle
│   └── fleet_vehicle.py     # Extends fleet.vehicle + new model fleet.vehicle.category
├── views/
│   └── fleet_vehicle_view.xml
├── data/
│   └── demo_data.xml
└── security/
    └── ir.model.access.csv
```

### car_rental_qatar_full (full application)

```
car_rental_qatar_full/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py          # Imports all models
│   ├── fleet_vehicle.py     # Extends fleet.vehicle (same idea as other module)
│   ├── rental_contract.py  # NEW model: rental.contract
│   ├── vehicle_inspection.py
│   ├── customer_document.py
│   └── rental_dashboard.py
├── views/
│   ├── fleet_vehicle_view.xml
│   ├── rental_contract_views.xml
│   ├── vehicle_inspection_views.xml
│   ├── customer_document_views.xml
│   └── rental_dashboard_views.xml
├── data/
│   ├── sequence.xml         # Number sequences (RC00001, INS00001)
│   └── vehicle_categories.xml  # Default categories (Economy, SUV, etc.)
├── reports/
│   └── fleet_utilization_report.xml
└── security/
    └── ir.model.access.csv
```

---

## 3. How Odoo Inheritance Works (Basics)

In Odoo there are two main ideas:

- **Extend an existing model** → use `_inherit = "existing.model"` (no new table; add fields/methods to the same model).
- **Create a new model** → use `_name = "your.model"`. You can still add behavior from other models with `_inherit = ['mail.thread', 'mail.activity.mixin']` (mixins).

### 3.1 Model inheritance: extending `fleet.vehicle`

Both modules **extend** the core Fleet model `fleet.vehicle`:

```python
# In both: car_rental_qatar/models/fleet_vehicle.py and car_rental_qatar_full/models/fleet_vehicle.py

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"   # ← We do NOT create a new model; we ADD to fleet.vehicle

    # New fields are ADDED to the existing fleet.vehicle table
    rental_state = fields.Selection([...], string="Rental Status", ...)
    rental_category_id = fields.Many2one("fleet.vehicle.category", ...)
    mulkiya_expiry = fields.Date(...)
    # ... etc
```

- **`_inherit = "fleet.vehicle"`** means: “Take the model `fleet.vehicle` (from the `fleet` app) and add these fields and methods to it.”
- There is still only one model: `fleet.vehicle`. No new table like `fleet_vehicle_extension`.
- So every vehicle record in the database gets `rental_state`, `rental_category_id`, etc.

### 3.2 New model: `fleet.vehicle.category`

Same file also defines a **new** model:

```python
class FleetVehicleCategory(models.Model):
    _name = "fleet.vehicle.category"   # ← NEW model (new table in DB)
    _description = "Vehicle Rental Category"

    name = fields.Char(...)
    daily_rate = fields.Float(...)
    # ...
```

- **`_name = "fleet.vehicle.category"`** means: “Create a new model (and table) with this technical name.”
- No `_inherit` here, so this is a brand‑new model, not an extension.

### 3.3 New model with mixin inheritance: `rental.contract`

In **car_rental_qatar_full**:

```python
class RentalContract(models.Model):
    _name = 'rental.contract'           # New model
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Add chatter + activities

    name = fields.Char(...)
    customer_id = fields.Many2one('res.partner', ...)
    # ...
```

- **`_name`**: new model `rental.contract` (new table).
- **`_inherit`**: list of **mixins**. You inherit:
  - **mail.thread**: chatter (messages, tracking).
  - **mail.activity.mixin**: activities (tasks, reminders).
- So `rental.contract` = your fields + all fields and behavior from those two mixins.

Summary:

- **Extend one model**: `_inherit = "model.name"` (single string), no `_name` for a new model.
- **New model**: `_name = "your.model"`.
- **New model + mixins**: `_name = "your.model"` and `_inherit = ['mixin1', 'mixin2']`.

---

## 4. View inheritance (XML)

You don’t copy the whole Fleet form; you **inherit** it and inject your fields/buttons.

### 4.1 Inherit an existing view

```xml
<record id="view_fleet_vehicle_form_inherit" model="ir.ui.view">
    <field name="name">fleet.vehicle.form.inherit</field>
    <field name="model">fleet.vehicle</field>
    <field name="inherit_id" ref="fleet.fleet_vehicle_view_form"/>   <!-- Parent view -->
    <field name="arch" type="xml">
        <!-- xpath: WHERE to change in the parent view -->
        <xpath expr="//div[@name='button_box']" position="inside">
            <button name="action_view_rentals" ...>
                <field name="rental_count" widget="statinfo" string="Rentals"/>
            </button>
        </xpath>
    </field>
</record>
```

- **inherit_id**: “This view extends `fleet.fleet_vehicle_view_form`.”
- **xpath expr**: “Find this node in the parent view.”
- **position="inside"**: “Add my content inside that node.”

So the original Fleet form is left in the `fleet` module; your module only adds a smart button and, in Full, a new notebook page.

### 4.2 XPath positions (quick reference)

- **inside** – append inside the node (default).
- **after** / **before** – add after/before the node.
- **replace** – replace the node.
- **attributes** – change attributes on the node.

Example: add columns after `license_plate` in the tree:

```xml
<xpath expr="//field[@name='license_plate']" position="after">
    <field name="rental_category_id"/>
    <field name="rental_daily_rate"/>
    <field name="rental_state" widget="badge" .../>
</xpath>
```

---

## 5. Other basics in these modules

### 5.1 Related fields

Value comes from a linked record:

```python
rental_daily_rate = fields.Float(
    related="rental_category_id.daily_rate",  # Same as category’s daily_rate
    store=True,
    readonly=True,
)
```

- **related**: path to another field (here: category → daily_rate).
- **store=True**: store in DB so you can search/group.
- **readonly=True**: user doesn’t edit it on the vehicle; they edit the category.

### 5.2 Computed fields

Value is calculated in Python:

```python
total_days = fields.Integer(compute='_compute_total_days', store=True)

@api.depends('pickup_date', 'return_date')
def _compute_total_days(self):
    for record in self:
        if record.pickup_date and record.return_date:
            delta = record.return_date - record.pickup_date
            record.total_days = max(1, delta.days)
        else:
            record.total_days = 0
```

- **compute**: method that sets the field.
- **@api.depends**: when to recompute (when these fields change).
- **store=True**: save in DB (optional; without it, computed on the fly).

### 5.3 Sequences (auto number for contracts)

In **data/sequence.xml**:

```xml
<record id="seq_rental_contract" model="ir.sequence">
    <field name="name">Rental Contract Sequence</field>
    <field name="code">rental.contract</field>
    <field name="prefix">RC</field>
    <field name="padding">5</field>
    <field name="number_next">1</field>
    <field name="number_increment">1</field>
</record>
```

In Python, when creating a contract:

```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('rental.contract') or 'New'
    return super(RentalContract, self).create(vals_list)
```

So each new contract gets a name like **RC00001**, **RC00002**, etc.

### 5.4 Security: `ir.model.access.csv`

Gives read/write/create/delete rights per model and group:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_rental_contract_user,access.rental.contract.user,model_rental_contract,base.group_user,1,1,1,1
```

- **model_id**: `model_<module>_<model_name>` (e.g. `model_rental_contract`).
- **group_id**: e.g. `base.group_user` (internal users).
- **perm_***: 1 = allow, 0 = deny.

You need one line per model you introduce (e.g. `rental.contract`, `fleet.vehicle.category` in Full). Extending `fleet.vehicle` doesn’t create a new model, so you don’t add access for “fleet.vehicle” again; you only add access for **new** models like `fleet.vehicle.category`.

### 5.5 Default data: `vehicle_categories.xml`

Loads default records for `fleet.vehicle.category`:

```xml
<record id="category_economy" model="fleet.vehicle.category">
    <field name="name">Economy</field>
    <field name="sequence">10</field>
    <field name="daily_rate">100.00</field>
    <field name="description">...</field>
</record>
```

- **model**: same as `_name` in Python (`fleet.vehicle.category`).
- **id**: XML id for this record (e.g. `car_rental_qatar_full.category_economy`). Used in views or code with `ref()`.

---

## 6. How the two modules differ (summary)

| Topic | car_rental_qatar | car_rental_qatar_full |
|--------|-------------------|------------------------|
| **Rental data** | Uses **car_rent** (`sale.rental.line`) | Own **rental.contract** model |
| **rental_count / action_view_rentals** | Counts `sale.rental.line` | Counts `rental.contract` |
| **Menus** | Adds “Vehicle Categories” under Fleet config | Full app menu: Contracts, Vehicles, Inspections, Documents, Reports |
| **Fleet form view** | Only smart button “Rentals” | Smart button + “Rental Information” notebook tab |
| **Dependencies** | base, fleet, **car_rent** | base, mail, fleet, sale_management, account, stock (no car_rent) |

The **Python inheritance pattern** (extending `fleet.vehicle`, new `fleet.vehicle.category`) is the same in both; the **business data** (which model stores rentals) and **menus/views** differ.

---

## 7. Loading order (for your study)

1. **`__manifest__.py`** – dependencies and list of data files (order matters for XML).
2. **`__init__.py`** (root) – imports `models`.
3. **`models/__init__.py`** – imports each model file (e.g. `fleet_vehicle`, `rental_contract`).
4. **Model files** – define/extend models (inheritance as above).
5. **Data files** – security, sequences, default categories, then views and menus (as in manifest).

With this you can trace: manifest → models load → data/views applied, and see how inheritance in both Python and XML extends Fleet and adds the rental logic step by step.
