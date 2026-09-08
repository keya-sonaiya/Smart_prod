-- Run this in the Supabase SQL editor AFTER SQLAlchemy has created the tables
-- (or after running the equivalent CREATE TABLE statements by hand).

-- ---------- Categories ----------
INSERT INTO categories (key, display_name, description) VALUES
('dining_table', 'Dining Table', 'Building or assembling a dining table from raw materials'),
('tv_mount', 'TV Wall Mount', 'Mounting a television on a wall');

-- ---------- Questions ----------
INSERT INTO category_questions (category_id, question_key, question_text, answer_type, enum_options, display_order) VALUES
(1, 'size', 'What size do you need (e.g. 4ft x 6ft)?', 'text', NULL, 1),
(1, 'material', 'Which material do you prefer?', 'enum', '["wood","metal"]', 2),
(1, 'seating', 'How many people should it seat?', 'number', NULL, 3);

INSERT INTO category_questions (category_id, question_key, question_text, answer_type, enum_options, display_order) VALUES
(2, 'tv_size', 'What is the TV size (in inches)?', 'number', NULL, 1),
(2, 'wall_type', 'What type of wall is it?', 'enum', '["concrete","drywall","brick"]', 2),
(2, 'mount_type', 'Do you need a fixed or adjustable wall mount?', 'enum', '["fixed","adjustable"]', 3),
(2, 'cable_mgmt', 'Do you want cable management accessories?', 'enum', '["yes","no"]', 4);

-- ---------- Products (dining table: ids 1-7, tv mount: ids 8-14, in insert order) ----------
INSERT INTO products (name, category_id, unit, attributes) VALUES
('Wooden Sheet', 1, 'sheet', '{"material":"wood"}'),
('Table Legs', 1, 'pcs', '{}'),
('Nut & Bolt Set', 1, 'set', '{}'),
('Wood Screws', 1, 'pcs', '{}'),
('Wood Glue', 1, 'bottle', '{}'),
('Sandpaper', 1, 'sheet', '{}'),
('Wood Polish', 1, 'bottle', '{}'),
('TV Wall Mount', 2, 'pcs', '{}'),
('Wall Plugs', 2, 'pcs', '{}'),
('Screws & Bolts', 2, 'set', '{}'),
('Drill Machine', 2, 'pcs', '{}'),
('Spirit Level', 2, 'pcs', '{}'),
('Cable Management Kit', 2, 'set', '{}'),
('HDMI Cable', 2, 'pcs', '{}');

-- ---------- Relationships: dining table ----------
INSERT INTO product_relationships (category_id, product_id, relation_type, quantity_formula, condition_json) VALUES
(1, 1, 'REQUIRES', '1', '{"material":"wood"}'),
(1, 2, 'REQUIRES', '4', '{}'),
(1, 3, 'REQUIRES', '1', '{}'),
(1, 4, 'REQUIRES', '12', '{"material":"wood"}'),
(1, 5, 'REQUIRES', '1', '{"material":"wood"}'),
(1, 6, 'REQUIRES', '2', '{"material":"wood"}'),
(1, 7, 'REQUIRES', '1', '{"material":"wood"}');

-- ---------- Relationships: TV mount ----------
INSERT INTO product_relationships (category_id, product_id, relation_type, quantity_formula, condition_json) VALUES
(2, 8, 'REQUIRES', '1', '{}'),
(2, 9, 'REQUIRES', '4', '{}'),
(2, 10, 'REQUIRES', '4', '{}'),
(2, 11, 'REQUIRES', '1', '{}'),
(2, 12, 'REQUIRES', '1', '{}'),
(2, 13, 'OPTIONAL', '1', '{"cable_mgmt":"yes"}'),
(2, 14, 'OPTIONAL', '1', '{}');

-- Seating affects the number of nut-and-bolt sets required.
UPDATE product_relationships
SET quantity_formula = 'seating/2'
WHERE product_id = (SELECT id FROM products WHERE name = 'Nut & Bolt Set'
					AND category_id = (SELECT id FROM categories WHERE key = 'dining_table'));

-- Sanity check after running: this should return the 7 dining-table items.
-- SELECT p.name, pr.quantity_formula, pr.condition_json
-- FROM product_relationships pr JOIN products p ON p.id = pr.product_id
-- WHERE pr.category_id = 1;
