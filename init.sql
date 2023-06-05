-- create table odds_bet365(
-- 	nome_pista text not null,
-- 	quando timestamp not null, -- data e hora da corrida
-- 	trap integer not null, -- 1,2,3,4,5,6
-- 	nome_galgo text null, -- nome do galgo para conferir se não foi subsituído
-- 	mercado text, -- back, bet, third, etc 
-- 	odd numeric(10,3), -- odd do momento, único valor que pode ser atualizado
-- 	primary key (nome_pista,quando,trap, mercado)
-- )

CREATE TABLE
  public.odds (
    nome_pista text NOT NULL,
    quando timestamp without time zone NOT NULL,
    trap integer NOT NULL,
    nome_galgo text NULL,
    mercado text NOT NULL,
    odd numeric(10, 3) NULL
  );
  
ALTER TABLE odds ADD CONSTRAINT odds_unique_constraint UNIQUE (nome_pista, quando, trap, nome_galgo, mercado);


