-- Run this AFTER the original seed_data.sql (dining_table + tv_mount already seeded).
-- Uses subqueries throughout instead of hardcoded IDs, so it's safe to run regardless
-- of what IDs the first two categories/products ended up with.

-- ==========================================================
-- CATEGORY: Living Room
-- ==========================================================
INSERT INTO categories (key, display_name, description) VALUES
('living_room', 'Living Room Furnishing', 'Furnishing or decorating a living room');

INSERT INTO category_questions (category_id, question_key, question_text, answer_type, enum_options, display_order)
SELECT id, 'room_size', 'What is your room size (e.g. 12ft x 14ft)?', 'text', NULL, 1
FROM categories WHERE key = 'living_room';

INSERT INTO category_questions (category_id, question_key, question_text, answer_type, enum_options, display_order)
SELECT id, 'budget', 'What is your budget?', 'enum', '["low","medium","high"]', 2
FROM categories WHERE key = 'living_room';

INSERT INTO category_questions (category_id, question_key, question_text, answer_type, enum_options, display_order)
SELECT id, 'style', 'Which style do you prefer?', 'enum', '["modern","traditional","minimalist","contemporary"]', 3
FROM categories WHERE key = 'living_room';

INSERT INTO category_questions (category_id, question_key, question_text, answer_type, enum_options, display_order)
SELECT id, 'occupants', 'How many people will use the room?', 'number', NULL, 4
FROM categories WHERE key = 'living_room';

INSERT INTO products (name, category_id, unit, attributes)
SELECT p.name, c.id, p.unit, '{}'::json
FROM categories c, (VALUES
    ('Sofa Set', 'set'),
    ('Coffee Table', 'pcs'),
    ('TV Unit', 'pcs'),
    ('Curtains', 'set'),
    ('Carpet', 'pcs'),
    ('Floor Lamp', 'pcs'),
    ('Wall Decor', 'set'),
    ('Indoor Plants', 'pcs')
) AS p(name, unit)
WHERE c.key = 'living_room';

INSERT INTO product_relationships (category_id, product_id, relation_type, quantity_formula, condition_json)
SELECT c.id, p.id, r.relation_type, r.qty, '{}'::json
FROM categories c
JOIN products p ON p.category_id = c.id
JOIN (VALUES
    ('Sofa Set', 'REQUIRES', '1'),
    ('Coffee Table', 'REQUIRES', '1'),
    ('TV Unit', 'REQUIRES', '1'),
    ('Curtains', 'REQUIRES', '2'),
    ('Carpet', 'REQUIRES', '1'),
    ('Floor Lamp', 'OPTIONAL', '1'),
    ('Wall Decor', 'OPTIONAL', '1'),
    ('Indoor Plants', 'OPTIONAL', '2')
) AS r(name, relation_type, qty) ON r.name = p.name
WHERE c.key = 'living_room';


-- ==========================================================
-- CATEGORY: Gaming PC
-- ==========================================================
INSERT INTO categories (key, display_name, description) VALUES
('gaming_pc', 'Gaming PC', 'Building a custom gaming or high-performance desktop PC');

INSERT INTO category_questions (category_id, question_key, question_text, answer_type, enum_options, display_order)
SELECT id, 'budget', 'What is your budget?', 'enum', '["budget","mid-range","high-end"]', 1
FROM categories WHERE key = 'gaming_pc';

INSERT INTO category_questions (category_id, question_key, question_text, answer_type, enum_options, display_order)
SELECT id, 'usage', 'Which games or applications will you use?', 'text', NULL, 2
FROM categories WHERE key = 'gaming_pc';

INSERT INTO category_questions (category_id, question_key, question_text, answer_type, enum_options, display_order)
SELECT id, 'rgb', 'Do you need RGB lighting?', 'enum', '["yes","no"]', 3
FROM categories WHERE key = 'gaming_pc';

INSERT INTO category_questions (category_id, question_key, question_text, answer_type, enum_options, display_order)
SELECT id, 'has_accessories', 'Do you already have a monitor and accessories?', 'enum', '["yes","no"]', 4
FROM categories WHERE key = 'gaming_pc';

INSERT INTO products (name, category_id, unit, attributes)
SELECT p.name, c.id, p.unit, '{}'::json
FROM categories c, (VALUES
    ('Processor (CPU)', 'pcs'),
    ('Motherboard', 'pcs'),
    ('RAM', 'pcs'),
    ('Graphics Card (GPU)', 'pcs'),
    ('SSD', 'pcs'),
    ('Power Supply', 'pcs'),
    ('PC Cabinet', 'pcs'),
    ('Cooling Fan', 'pcs'),
    ('Keyboard', 'pcs'),
    ('Mouse', 'pcs'),
    ('RGB Lighting Kit', 'set')
) AS p(name, unit)
WHERE c.key = 'gaming_pc';

-- Core components: always required, no condition
INSERT INTO product_relationships (category_id, product_id, relation_type, quantity_formula, condition_json)
SELECT c.id, p.id, r.relation_type, r.qty, '{}'::json
FROM categories c
JOIN products p ON p.category_id = c.id
JOIN (VALUES
    ('Processor (CPU)', 'REQUIRES', '1'),
    ('Motherboard', 'REQUIRES', '1'),
    ('RAM', 'REQUIRES', '2'),
    ('Graphics Card (GPU)', 'REQUIRES', '1'),
    ('SSD', 'REQUIRES', '1'),
    ('Power Supply', 'REQUIRES', '1'),
    ('PC Cabinet', 'REQUIRES', '1'),
    ('Cooling Fan', 'REQUIRES', '2')
) AS r(name, relation_type, qty) ON r.name = p.name
WHERE c.key = 'gaming_pc';

-- Conditional: only suggest keyboard/mouse if they DON'T already have accessories
INSERT INTO product_relationships (category_id, product_id, relation_type, quantity_formula, condition_json)
SELECT c.id, p.id, 'OPTIONAL', '1', '{"has_accessories":"no"}'::json
FROM categories c
JOIN products p ON p.category_id = c.id AND p.name IN ('Keyboard', 'Mouse')
WHERE c.key = 'gaming_pc';

-- Conditional: only suggest the RGB kit if they said yes to RGB
INSERT INTO product_relationships (category_id, product_id, relation_type, quantity_formula, condition_json)
SELECT c.id, p.id, 'OPTIONAL', '1', '{"rgb":"yes"}'::json
FROM categories c
JOIN products p ON p.category_id = c.id AND p.name = 'RGB Lighting Kit'
WHERE c.key = 'gaming_pc';

-- ==========================================================
-- Sanity checks — run these after the inserts above
-- ==========================================================
-- SELECT p.name, pr.relation_type, pr.quantity_formula, pr.condition_json
-- FROM product_relationships pr
-- JOIN products p ON p.id = pr.product_id
-- JOIN categories c ON c.id = pr.category_id
-- WHERE c.key = 'living_room';

-- SELECT p.name, pr.relation_type, pr.quantity_formula, pr.condition_json
-- FROM product_relationships pr
-- JOIN products p ON p.id = pr.product_id
-- JOIN categories c ON c.id = pr.category_id
-- WHERE c.key = 'gaming_pc';
