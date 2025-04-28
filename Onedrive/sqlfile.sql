CREATE TABLE maincalls (
    request_id SERIAL PRIMARY KEY,
    type_request VARCHAR(10),
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    phone VARCHAR(14),
    comment_req VARCHAR(200),
    service VARCHAR(30),
    sources VARCHAR(30),
    fio VARCHAR(80),
    links VARCHAR(500)
);

