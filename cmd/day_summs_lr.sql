USE utrack_db;
CREATE view t1 AS 
(SELECT DATE(TIME) AS 'time', id as "id", COUNT(*) as recNum_A, SUM(Length) as "Summ_A" , 
SUM(case when status=3 then length else null end) as "Work_A", 
SUM(case when status=2 then length else null end) as "StandBy_A", 
SUM(case when status=1 then length else null end) as "Off_A",
SUM(case when STATUS=0 then length else null end) as "NA_A"
from track_lr 
  where time BETWEEN (date(NOW())-INTERVAL 31 MINUTE ) AND  (date(NOW()) + INTERVAL 7 HOUR - INTERVAL 1 minute)
group BY id);
CREATE VIEW t2 AS 
(select DATE(TIME) AS 'time', id as "id", COUNT(*) as recNum_B, SUM(Length) as "Summ_B", 
SUM(case when status=3 then length else null end) as "Work_B", 
SUM(case when status=2 then length else null end) as "StandBy_B", 
SUM(case when status=1 then length else null end) as "Off_B",
SUM(case when STATUS=0 then length else null end) as "NA_B" 
from track_lr
  where time BETWEEN date(NOW())+INTERVAL 7 hour- INTERVAL 1 minute and  date(NOW()) + INTERVAL 15 HOUR + INTERVAL 29 minute
group BY id);
CREATE VIEW t3 AS 
(select DATE(TIME) AS 'time', id as "id", COUNT(*) as recNum_c, SUM(Length) as "Summ_c", 
SUM(case when status=3 then length else null end) as "Work_c", 
SUM(case when status=2 then length else null end) as "StandBy_c", 
SUM(case when status=1 then length else null end) as "Off_c",
SUM(case when STATUS=0 then length else null end) as "NA_C" 
from track_lr
  where time BETWEEN date(NOW())+INTERVAL 15 HOUR + INTERVAL 29 minute and  date(NOW()) +INTERVAL 23 HOUR + INTERVAL 29 minute 
group BY id);

create VIEW vt AS
(SELECT ifnull (TIME1,TIME2) AS time, ifnull (id1,id2) AS id, NA_A, Off_A, Standby_A, Work_A,NA_B, Off_B, Standby_B, Work_B  from
(
SELECT  t1.time AS time1, t1.id AS id1, t1.NA_A, t1.Off_A, t1.Standby_A, t1.Work_A,
      t2.time AS TIME2, t2.id AS id2, t2.NA_B, t2.Off_B, t2.Standby_B, t2.Work_B 
		FROM t1 left JOIN t2 ON t1.id=t2.id
UNION 
SELECT  t1.time AS time1, t1.id AS id1, t1.NA_A, t1.Off_A, t1.Standby_A, t1.Work_A, 
        t2.time AS TIME2, t2.id AS id2,t2.NA_B, t2.Off_B, t2.Standby_B, t2.Work_B  
     FROM t2 left JOIN t1 on t1.id=t2.id
) AS tbl1 );

INSERT INTO summdata_lr (daydate, id, NA_A, Off_A, Standby_A, Work_A, NA_B, Off_B, Standby_B, Work_B, NA_c, Off_c, Standby_c, Work_c)
SELECT date(NOW()) AS daydate, ifnull (id,id3) AS id, NA_A, Off_A, Standby_A, Work_A,NA_B, Off_B, Standby_B, Work_B, NA_C, Off_C, Standby_C, Work_C  from
(
SELECT  vt.time AS time, vt.id AS id, vt.NA_A, vt.Off_A, vt.Standby_A, vt.Work_A, vt.NA_B, vt.Off_B, vt.Standby_B, vt.Work_B, 
        t3.time AS TIME3, t3.id AS id3, t3.NA_C, t3.Off_C, t3.Standby_C, t3.Work_C 
       FROM vt left JOIN t3 ON vt.id=t3.id 
UNION 
SELECT  vt.time AS time, vt.id AS id, vt.NA_A, vt.Off_A, vt.Standby_A, vt.Work_A, vt.NA_B, vt.Off_B, vt.Standby_B, vt.Work_B,
        t3.time AS TIME3, t3.id AS id3, t3.NA_C, t3.Off_C, t3.Standby_C, t3.Work_C
       FROM t3 left JOIN vt ON vt.id=t3.id 
) AS tbl2;
DROP VIEW t1,t2,t3,vt;