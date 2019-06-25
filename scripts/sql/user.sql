\c asgard;

insert into account (name, namespace, owner) values ('Asgard/INFRA', 'asgard-infra', 'asgard-infra');
insert into account (name, namespace, owner) values ('Asgard/DEV', 'asgard-dev', 'asgard-dev');
insert into account (name, namespace, owner) values ('Asgard/Core', 'asgard', 'asgard');

INSERT INTO "user" (tx_name, tx_email, tx_authkey, bl_system) VALUES ('Dalton Barreto', 'daltonmatos@gmail.com', '15ce068d5d2942b18a7f8ae76933f53', false);
INSERT into "user" (tx_name, tx_email, tx_authkey, bl_system) values ('Rafael Amorim', 'rafael@admatic.com.br', 'cccccchcdhjrtrgbtndbedljrectjhv', false);
INSERT INTO "user" (tx_name, tx_email, tx_authkey, bl_system) VALUES ('Lucas Domingues', 'lucas.domingues@b2wdigital.com', 'd8c336eb8cca4d39a8425a151ac84f81', false);
INSERT INTO "user" (tx_name, tx_email, tx_authkey, bl_system) VALUES ('Vitor Santos', 'vitor.asantos@b2wdigital.com', '984a42361c8c485991b151ba5a81c97f', false);
INSERT INTO "user" (tx_name, tx_email, tx_authkey, bl_system) VALUES ('Thales Sathler', 'thales.lima@b2wdigital.com', '0a37a4450ab5461e954f94456138d033', false);

INSERT INTO user_has_account (account_id, user_id) VALUES (
  (SELECT id from account where name = 'Asgard/DEV'),
  (SELECT id from "user" where tx_email='daltonmatos@gmail.com')
);

INSERT INTO user_has_account (account_id, user_id) VALUES (
  (SELECT id from account where name = 'Asgard/INFRA'),
  (SELECT id from "user" where tx_email='daltonmatos@gmail.com')
);

INSERT INTO user_has_account (account_id, user_id) VALUES (
  (SELECT id from account where name = 'Asgard/Core'),
  (SELECT id from "user" where tx_email='daltonmatos@gmail.com')
);

INSERT INTO user_has_account (account_id, user_id) VALUES (
  (SELECT id from account where name = 'Asgard/DEV'),
  (SELECT id from "user" where tx_email='rafael@admatic.com.br')
);

INSERT INTO user_has_account (account_id, user_id) VALUES (
  (SELECT id from account where name = 'Asgard/INFRA'),
  (SELECT id from "user" where tx_email='rafael@admatic.com.br')
);

INSERT INTO user_has_account (account_id, user_id) VALUES (
  (SELECT id from account where name = 'Asgard/DEV'),
  (SELECT id from "user" where tx_email='lucas.domingues@b2wdigital.com')
);

INSERT INTO user_has_account (account_id, user_id) VALUES (
  (SELECT id from account where name = 'Asgard/INFRA'),
  (SELECT id from "user" where tx_email='lucas.domingues@b2wdigital.com')
);

INSERT INTO user_has_account (account_id, user_id) VALUES (
  (SELECT id from account where name = 'Asgard/Core'),
  (SELECT id from "user" where tx_email='vitor.asantos@b2wdigital.com')
);

INSERT INTO user_has_account (account_id, user_id) VALUES (
  (SELECT id from account where name = 'Asgard/DEV'),
  (SELECT id from "user" where tx_email='vitor.asantos@b2wdigital.com')
);

INSERT INTO user_has_account (account_id, user_id) VALUES (
  (SELECT id from account where name = 'Asgard/INFRA'),
  (SELECT id from "user" where tx_email='vitor.asantos@b2wdigital.com')
);

INSERT INTO user_has_account (account_id, user_id) VALUES (
  (SELECT id from account where name = 'Asgard/Core'),
  (SELECT id from "user" where tx_email='thales.lima@b2wdigital.com')
);

INSERT INTO user_has_account (account_id, user_id) VALUES (
  (SELECT id from account where name = 'Asgard/DEV'),
  (SELECT id from "user" where tx_email='thales.lima@b2wdigital.com')
);

INSERT INTO user_has_account (account_id, user_id) VALUES (
  (SELECT id from account where name = 'Asgard/INFRA'),
  (SELECT id from "user" where tx_email='thales.lima@b2wdigital.com')
);
