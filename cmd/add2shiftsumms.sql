USE utrack_db;

DROP VIEW IF EXISTS t1,t2, tC1, tC2, tC1_2, tt1_2,t  ;
CREATE view t1 AS 
(SELECT DATE(TIME) AS 'time', id as "id", 
SUM(case when status=3 then length else null end) as "Work_1", 
SUM(case when status=2 then length else null end) as "StandBy_1", 
SUM(case when status=1 then length else null end) as "Off_1",
SUM(case when STATUS=0 then length else null end) as "NA_1"
from track_lr 
  where time BETWEEN (DATE(NOW())-INTERVAL 17 HOUR ) AND  (DATE(NOW()) - INTERVAL 5 HOUR )
group BY id);



CREATE view tC1 AS 
(SELECT DATE(TIME) AS 'time', id as "id", 
SUM(case when STATUS=7 then length else null end) as "Counter_1"
from track_lr 
  where time BETWEEN (DATE(NOW())-INTERVAL 17 HOUR + INTERVAL 1 minute ) AND  (DATE(NOW()) - INTERVAL 5 HOUR + INTERVAL 1 minute)
group BY id);



CREATE VIEW t2 AS 
(select DATE(TIME) AS 'time', id as "id", 
SUM(case when status=3 then length else null end) as "Work_2", 
SUM(case when status=2 then length else null end) as "StandBy_2", 
SUM(case when status=1 then length else null end) as "Off_2",
SUM(case when STATUS=0 then length else null end) as "NA_2" 
from track_lr 
  where time BETWEEN DATE(NOW())- INTERVAL 5 hour- INTERVAL 1 minute and DATE(NOW()) + INTERVAL 7 HOUR - INTERVAL 1 minute
group BY id);



CREATE view tC2 AS 
(SELECT DATE(TIME) AS 'time', id as "id", 
SUM(case when STATUS=7 then length else null end) as "Counter_2"
from track_lr 
  where time BETWEEN DATE(NOW())-INTERVAL 5 HOUR + INTERVAL 1 minute and DATE(NOW()) + INTERVAL 7 HOUR + INTERVAL 1 minute
group BY id);

CREATE view tC1_2 AS 
(SELECT ifnull (TIME1,TIME2) AS time, ifnull (id1,id2) AS id, Counter_1,Counter_2  from
(
SELECT  tC1.time AS time1,  tC1.id AS id1,  tC1.Counter_1, tC2.time AS time2,  tC2.id AS id2,  tC2.Counter_2
		FROM tC1 left JOIN tC2 ON tc1.id=tc2.id
UNION 
SELECT  tC1.time AS time1,  tC1.id AS id1,  tC1.Counter_1, tC2.time AS time2,  tC2.id AS id2,  tC2.Counter_2
		FROM tC2  LEFT JOIN tC1 ON tc1.id=tc2.id  
 ) AS tb1_counters );


CREATE view tt1_2 AS 
(SELECT ifnull (TIME1,TIME2) AS time, ifnull (id1,id2) AS id, NA_1, Off_1, Standby_1, Work_1, NA_2, Off_2, Standby_2, Work_2 FROM
(
SELECT  t1.time AS time1, t1.id AS id1, t1.NA_1, t1.Off_1, t1.Standby_1, t1.Work_1,
        t2.time AS TIME2, t2.id AS id2, t2.NA_2, t2.Off_2, t2.Standby_2, t2.Work_2 
		FROM t1 left JOIN t2 ON t1.id=t2.id
UNION
SELECT  t1.time AS time1, t1.id AS id1, t1.NA_1, t1.Off_1, t1.Standby_1, t1.Work_1,
        t2.time AS TIME2, t2.id AS id2, t2.NA_2, t2.Off_2, t2.Standby_2, t2.Work_2 
		FROM t2 left JOIN t1 ON t2.id=t1.id
 ) AS tb1_time );

CREATE view t AS 
 (SELECT  id,  NA_1, Off_1, Standby_1, Work_1, NA_2, Off_2, Standby_2, Work_2, Counter_1, Counter_2 from
(SELECT  tt1_2.time AS time, tt1_2.id AS id, tt1_2.NA_1, tt1_2.Off_1, tt1_2.Standby_1, tt1_2.Work_1, tt1_2.NA_2, tt1_2.Off_2, tt1_2.Standby_2, tt1_2.Work_2,
         tC1_2.time AS TIME2,  tC1_2.id AS id2, tC1_2.Counter_1, tC1_2.Counter_2
		FROM tt1_2 left JOIN tC1_2 ON tt1_2.id=tC1_2.id
UNION
SELECT  tt1_2.time AS time, tt1_2.id AS id, tt1_2.NA_1, tt1_2.Off_1, tt1_2.Standby_1, tt1_2.Work_1, tt1_2.NA_2, tt1_2.Off_2, tt1_2.Standby_2, tt1_2.Work_2,
         tC1_2.time AS TIME2,  tC1_2.id AS id2, tC1_2.Counter_1, tC1_2.Counter_2
		FROM tc1_2 left JOIN tt1_2 ON tc1_2.id=tt1_2.id) AS tt);

#SELECT * from t;

UPDATE summdata_lr SET NA_1=(select NA_1 FROM t WHERE id=summdata_lr.id) , Off_1=(select Off_1 FROM t WHERE id=summdata_lr.id), 
								Standby_1= (select Standby_1 FROM t WHERE id=summdata_lr.id), Work_1=(select Work_1 FROM t WHERE id=summdata_lr.id), 
								NA_2=(select NA_2 FROM t WHERE id=summdata_lr.id), Off_2=(select Off_2 FROM t WHERE id=summdata_lr.id), 
								Standby_2=(select Standby_2 FROM t WHERE id=summdata_lr.id), Work_2=(select Work_2 FROM t WHERE id=summdata_lr.id), 
								Counter_1=(select Counter_1 FROM t WHERE id=summdata_lr.id), Counter_2=(select Counter_2  FROM t WHERE id=summdata_lr.id)
WHERE daydate=DATE(NOW())-INTERVAL 1 DAY AND id IN (select id from t);



DROP VIEW IF EXISTS t1,t2, tC1, tC2, tC1_2, tt1_2,t ;