-- select count(*)
-- from validations;

select valid, 
	cnt, 100.0*cnt/(sum(cnt) OVER ()) as pct
from (select valid, count(*) as cnt from validations group by valid) foo;
