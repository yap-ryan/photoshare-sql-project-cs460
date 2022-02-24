CREATE DATABASE IF NOT EXISTS photoshareTEST2;
USE photoshareTEST2;

CREATE TABLE User(
  user_id INTEGER AUTO_INCREMENT, 
  password CHAR(10), 
  gender CHAR(1), 
  first_name VARCHAR(20), 
  last_name VARCHAR(20), 
  email VARCHAR(20) UNIQUE,
	date_of_birth DATE, 
	hometown VARCHAR(20), 
	contribution_score INTEGER, 

	PRIMARY KEY (user_id), 

	CHECK (contribution_score >= 0), 
	CHECK (gender='f' OR gender='m' OR gender='n')
); 

CREATE TABLE Friendship(
  requestor_id INTEGER NOT NULL,
  addressee_id INTEGER NOT NULL,


	PRIMARY KEY (requestor_id, addressee_id),
	FOREIGN KEY (requestor_id) 
	REFERENCES User(user_id),
	FOREIGN KEY (addressee_id) 
	REFERENCES User(user_id),
	CHECK (requestor_id <> addressee_id)
);


CREATE TABLE Album(
  album_id INTEGER AUTO_INCREMENT, 
  name VARCHAR(20), 
  creation_date DATE, 

  user_id INTEGER NOT NULL, 

  PRIMARY KEY (album_id),
  FOREIGN KEY (user_id) 
  REFERENCES User(user_id)
); 



CREATE TABLE Photo(
  photo_id INTEGER AUTO_INCREMENT,
  data VARCHAR(255) NOT NULL,
  caption VARCHAR(255),
  likes INTEGER, 
  album_id INTEGER NOT NULL, 

  PRIMARY KEY (photo_id),
  FOREIGN KEY (album_id)
      REFERENCES Album(album_id)
      ON DELETE CASCADE,
	CHECK (likes >= 0)    
);


CREATE TABLE Comment(
    comment_id INTEGER AUTO_INCREMENT,
    text VARCHAR(255),
    date DATE,
    user_id INTEGER NOT NULL,
    photo_id INTEGER NOT NULL,

    PRIMARY KEY (comment_id),
    FOREIGN KEY (user_id) 
		REFERENCES User(user_id),
    FOREIGN KEY (photo_id) 
		REFERENCES Photo(photo_id)
		ON DELETE CASCADE
);


CREATE TABLE Tag(
    text VARCHAR(100), 
    photo_id INTEGER NOT NULL, 

    PRIMARY KEY (text, photo_id), 
    FOREIGN KEY (photo_id) 
		REFERENCES Photo(photo_id) 
		ON DELETE CASCADE
); 