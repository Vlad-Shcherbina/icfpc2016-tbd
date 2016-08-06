DROP TABLE IF EXISTS quotas;
DROP TABLE IF EXISTS requests;
DROP TYPE IF EXISTS endpoint;

CREATE TYPE endpoint AS ENUM ( 'hello'
                             , 'blob'
                             , 'snapshot/list'
                             , 'problem/submit'
                             , 'solution/submit'
                             );

CREATE TABLE IF NOT EXISTS requests (
   id          bigserial 			 NOT NULL PRIMARY KEY
  ,endpoint    endpoint        NOT NULL
  ,payload     json            NULL
  ,result      json            NULL
  ,priority    int             NOT NULL DEFAULT(1)
);

CREATE TABLE IF NOT EXISTS quotas (
	 endpoint		endpoint				 NOT NULL PRIMARY KEY
	,quota			int						 	 NOT NULL DEFAULT(1000)
)
