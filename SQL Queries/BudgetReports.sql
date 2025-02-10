SELECT 
    c.id AS contact_id,
    c.name AS contact_name,
    c.email AS contact_email,
    b.id AS budget_id,
    b.budget_name,
    b.total_budget,
    b.current_spent,
    b.remaining_budget,
    b.start_date,
    b.end_date,
    b.currency AS budget_currency,
    b.status AS budget_status,
    bl.id AS line_item_id,
    bl.line_item_name,
    bl.allocated_amount,
    bl.spent_amount,
    bl.remaining_amount AS line_item_remaining_amount,
    bl.status AS line_item_status,
    bl.created_at AS line_item_created_at
FROM contacts c
JOIN budgets b ON c.id = b.contact_id
LEFT JOIN budget_line_items bl ON b.id = bl.budget_id
ORDER BY c.id, b.id, bl.id;
