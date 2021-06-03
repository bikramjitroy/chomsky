

CREATE TABLE bot_flow_diagram (
    id varchar (50) PRIMARY KEY,
    bot_id varchar (50) NOT NULL,
    bot_type varchar (50) NOT NULL,
    bot_diagram json NOT NULL,
    bot_diagram_schema_version varchar (50) NOT NULL,
    description varchar (50) NOT NULL,
    creation_time timestamp without time zone NOT NULL
);
