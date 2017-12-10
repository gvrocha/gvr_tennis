PRAGMA page_size;
PRAGMA page_size = 65536;
PRAGMA page_size;
CREATE TABLE IF NOT EXISTS ranking      (date date, 
                                         mode text,
                                         ranking real,
                                         player text,
                                         points real,
                                         tour_played integer,
                                         country text,
                                         player_tag text,
                                         player_code text);

CREATE TABLE IF NOT EXISTS ranking_date (date date, 
                                         mode text);
