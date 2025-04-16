CREATE TABLE requests (
    request_id SERIAL PRIMARY KEY,
    type_request VARCHAR(20),
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    phone VARCHAR(20),
    comment_req VARCHAR(200),
    service VARCHAR(50),
    sources VARCHAR(30),
    fio VARCHAR(100),
    links VARCHAR(500)
);

