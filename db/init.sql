CREATE DATABASE userData;
use userData;

CREATE TABLE IF NOT EXISTS tbluserDataImport (

    `username` VARCHAR(40),
    `emailaddress` VARCHAR(40),
    `password` VARCHAR(40),
    PRIMARY KEY (username)

);

INSERT INTO tbluserDataImport (username, emailaddress, password) VALUES
    (DannyD, dannyd@gmail.com, 9sd9a9da2),
    (dantespeak, dantespeak@gmail.com, dudebro),
    (Blastermaster, blastermaster99@hotmail.com, cheerios),