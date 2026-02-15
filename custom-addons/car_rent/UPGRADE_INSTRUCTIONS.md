# Car Rent Module - Upgrade Instructions

## What's Fixed
- Vehicle rental details now appear in quotation and invoice PDFs
- Professional report layout with all rental information
- Proper integration with Odoo's invoicing workflow

## Installation Steps

1. **Restart Odoo** (to load new files):
   ```bash
   docker-compose restart
   ```

2. **Upgrade the module**:
   - Go to Apps menu
   - Remove "Apps" filter
   - Search for "CAR RENT"
   - Click "Upgrade" button

3. **Test the fix**:
   - Open Sales > Orders > Quotations
   - Create or open a quotation
   - Add vehicle rental lines
   - Click "Preview" or "Send by Email"
   - Verify vehicle details appear in the PDF

## How It Works

### For Quotations:
- Vehicle rental details display in a dedicated table
- Shows: Vehicle, Pickup Location, Dates, Days, Rate, Subtotal

### For Invoices:
- When you create an invoice, rental details are preserved
- Invoice PDF shows the same rental information table

### Automatic Sync:
- When you confirm a quotation, rental lines automatically create sale order lines
- This ensures proper invoicing and accounting

## Optional: Manual Sync
If you need to preview order lines before confirming:
- Click "Update Order Lines" button in the Vehicle Rental tab
- This creates/updates sale order lines from rental data

## Notes
- Old quotations will still work
- The module now depends on 'account' module (for invoice reports)
- A default "Vehicle Rental Service" product is created automatically
