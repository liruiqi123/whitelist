yesterday=`date +%Y%m%d`
monthday=`date -d '-6 months' +%Y%m%d`

#yesterday='20171026'
#monthday='20170726'

echo $yesterday
echo $monthday

hive -e " use kg; 




drop table temp_white_list_stp1; 
drop table temp_white_list_stp2; 
drop table temp_white_list_stp3; 
drop table temp_white_list_stp4; 
drop table temp_white_list_stp5;
drop table temp_white_list_stp6;
drop table temp_white_list_stp7; 
drop table temp_white_list_stp8; 
drop table temp_white_list_stp9;
drop table temp_white_list_stp10;
drop table temp_white_list_stp11;


drop table temp_white_list_stp11;
drop table temp_white_list_stp11_last_house_condition;
drop table temp_white_list_stp11_last_max_diploma;
drop table temp_white_list_stp11_delay_per_overdue_term_1;
drop table temp_white_list_stp11_delay_per_overdue_term_2;
drop table temp_white_list_stp11_delay_per_overdue_term_3;
drop table temp_white_list_stp11_unpaid_prin_rate_1;
drop table temp_white_list_stp11_unpaid_prin_rate_2;
drop table temp_white_list_stp11_unpaid_prin_rate_3;
drop table temp_white_list_stp12_score_1;
drop table temp_white_list_stp12_score_2;


create table temp_white_list_stp1 as
select t1.* from
(select
uuid	,
source	,
transport_id	,
name	,
user_id	,
id_number	,
mobile	,
mobile2	,
apply_time	,
apply_device_id	,
apply_id	,
apply_ip	,
apply_department_name	,
apply_department_city	,
apply_latitude	,
apply_longitude	,
bank_card_num	,
bank_name	,
invite_code	,
invite_code_data	,
invite_mobile	,
is_expand	,
amortisation	,
product_type	,
loan_purpose	,
loan_type	,
register_time	,
register_city	,
register_detail_address	,
register_latitude	,
register_longitude	,
register_province	,
register_device_id	,
register_ip	,
resident_duration	,
resident_city	,
resident_detail_address	,
resident_district	,
resident_province	,
resident_area_code	,
resident_full_number	,
resident_number	,
resident_status	,
sales_person_name	,
sfz_edit_count	,
sfz_error_count	,
org_name	,
org_detail_address	,
org_provice	,
org_city	,
org_district	,
org_area_code	,
org_full_number	,
org_number	,
occupation	,
salary	,
credit_card_or_load	,
domicile_city	,
domicile_detail_address	,
domicile_district	,
domicile_provice	,
email	,
house_city	,
house_detail_address	,
house_district	,
house_province	,
marriage	,
max_diploma	,
qq	,
social_insurance	,
total_amount	,
process_status	,
borrow_amount	,
borrow_status	,
contract_id	,
end_date	,
decision_desc	,
decision_inhand_amount	,
decision_amount	,
decision_month_return	,
decision_loan_term	,
cashier_time	,
month_return	,
paid_amount	,
refuse_code	,
repay_time	,
complete_type	,
return_list	,
current_overdue_days	,
current_term_expect_amount	,
last_term_status	,
max_overdue_days	,
owed_contract_amount	,
owed_contract_corpus	,
recent_12_terms	,
recent_24_terms	,
returned_terms	,
total_overdue_count	,
kg.total_overdue_days(return_list) as total_overdue_days,
contacts
from mortgagor_$yesterday t3
where source = 'ce_clic'
and product_type in ('精英贷','新薪贷','新薪宜楼贷','新薪贷(低)'
,'新薪贷（银行合作）','精英贷（银行合作）' ,'助业贷','助业宜楼贷','授薪','自雇','车主现金贷')) t1
inner join
(select id_number,max(apply_time) apply_time from mortgagor_$yesterday t1
where source = 'ce_clic'
and product_type in ('精英贷','新薪贷','新薪宜楼贷','新薪贷(低)'
,'新薪贷（银行合作）','精英贷（银行合作）' ,'助业贷','助业宜楼贷','授薪','自雇','车主现金贷') and cashier_time != ''
group by id_number) t2
on (t1.id_number = t2.id_number  and t1.apply_time  = t2.apply_time);


create table  temp_white_list_stp2 as
select t1.* , t2.busimode,t2.issueamt,t2.customerid,t2.settledate,t2.contractamt,t2.feeflag,account_source from temp_white_list_stp1 t1
inner join
(select tt1.applyid,tt1.busimode,tt1.issueamt,tt1.customerid,tt1.settledate,tt1.contractamt,tt1.feeflag,
case when tt1.busimode = '03' and  tt1.Movflag = '0' then '0'
when tt1.busimode = '01' then '1'
when tt1.busimode = '02' then '2'
when tt1.busimode = '03' and  tt1.Movflag = '1' then '3'
when tt1.busimode = '07' then '4'
when tt1.busimode = '08' and tt1.bankid = '0316' then '5'
when tt1.busimode = '10' then '8'
when tt1.busimode = '08' and tt1.channecode in ('1','2') and tt1.bankid = '0530' then '9'
when tt1.busimode = '03' and tt1.trustcompno = '181' then '10'
when tt1.busimode = '03' and tt1.trustcompno = '1'  then '11'
when tt1.busimode = '08' and tt1.bankid = '0530' and tt1.channecode = '107' then '12'
else ''  end   as account_source
from whitelist_xhx_lnscontractinfo_part tt1
inner join
( select max(sysmoddate) dt ,applyid from whitelist_xhx_lnscontractinfo_part group by applyid ) tt2
on (tt1.applyid = tt2.applyid and tt1.sysmoddate = tt2.dt)
) t2
on (t1.apply_id = t2.applyid);


create table temp_white_list_stp3 as
select t3.transport_id,t3.has_car,t4.house_status,t3.birthday,t3.credit_level,t3.id_number,t3.house_condition,t3.max_diploma from (
select t1.mortgagor_id,t1.transport_id,t2.credit_level,
t1.has_car,t1.birthday ,t1.id_number,t1.house_condition,t1.max_diploma
from whitelist_clic_tc_mortgagor_data t1
inner join (
select
t1.transport_id ,t1.credit_level
from
(select * from whitelist_clic_tc_credit_grade_part
where credit_level_version = '3_shouxin') t1
inner  join
(select max(credit_grade_id) credit_grade_id,transport_id from whitelist_clic_tc_credit_grade_part
where credit_level_version = '3_shouxin'
group by transport_id ) t2
on (t1.transport_id = t2.transport_id  and t1.credit_grade_id = t2.credit_grade_id)
) t2
on (t1.transport_id = t2.transport_id and t1.mortgagor_type = '0') ) t3
inner join
whitelist_clic_tc_mortgagor_data t4
on (t3.mortgagor_id= t4.mortgagor_id and t4.mortgagor_type = '0');


create table  temp_white_list_stp4
as select t2.birthday,t1.*,t2.house_status,t2.has_car,t2.credit_level,t2.house_condition,t2.max_diploma
from
temp_white_list_stp2 t1
inner join
temp_white_list_stp3 t2
on (t1.transport_id = t2.transport_id and t1.id_number = t2.id_number);

create table temp_white_list_stp5 as
select t1.* from temp_white_list_stp4 t1
left join
(select distinct id_number
from mortgagor_$yesterday
where loan_type = '循环贷'
and product_type in ('精英贷','新薪贷','新薪宜楼贷','新薪贷(低)'
,'新薪贷（银行合作）','精英贷（银行合作）' ,'助业贷','精英贷（农贷）','助业宜楼贷','授薪','自雇')
and replace(substr(apply_time,1,10),'-', '')  >= '$monthday'
and process_status like '%拒%') t2
on (t1.id_number = t2.id_number)
where t2.id_number  is null;

create table temp_white_list_stp6
as
select sum(case when borrow_status like '%结清%'
then 0 else  nvl(current_expect_prepayamt(return_list),0) end) as prepay,id_number
from mortgagor_$yesterday
where source = 'ce_clic'
and product_type in ('精英贷','新薪贷','新薪宜楼贷','新薪贷(低)'
,'新薪贷（银行合作）','精英贷（银行合作）' ,'助业贷','助业宜楼贷','授薪','自雇')
and return_list is not null
group by id_number;


create table temp_white_list_stp7 as
select t1.*,t2.prepay
from
temp_white_list_stp5  t1
left join
temp_white_list_stp6 t2
on (t1.id_number  = t2.id_number ); "

hadoop fs -mv /user/yisou/jiajincao/white_list_in /user/yisou/jiajincao/white_list_in_${yesterday}

hive -e "
use kg;

CREATE TABLE temp_white_list_stp8 as
SELECT t1.*, t2.smp_office_id
FROM temp_white_list_stp7 t1
LEFT JOIN
(select applyid,smp_office_id from  sellmanager_tsm_apply_smp_department_external_part) t2
ON t1.apply_id = t2.applyid ;


create table temp_white_list_stp9 as
SELECT t1.*
FROM temp_white_list_stp8 t1
    LEFT JOIN (SELECT kg.decode(sfz_id, 'yisou') AS id_number
        FROM blacklist_$yesterday
        WHERE sfz_id IS NOT NULL
        group by sfz_id
        ) t2 ON t1.id_number = t2.id_number
WHERE t2.id_number IS NULL;


create table temp_white_list_stp10 as
SELECT t1.*
FROM temp_white_list_stp9 t1
where 1=1
and length(mobile) = 11
and mobile like '1%';


create table temp_white_list_stp11 as
select
transport_id, house_condition,max_diploma2,contractamt,settledate ,
one_return['returnDate']  as repayownbdate,
one_return['returnTime'] as termretdate,
one_return['acctFlag'] as acctflag,
one_return['isOverdue'] as delayflag,
one_return['expectReturnCorpus']  as termretprin
from (
    select transport_id, house_condition,max_diploma2,contractamt,settledate, one_return
    from kg.temp_white_list_stp10
    lateral view explode(kg.from_json(kg.my_unzip(return_list), 'array<map<string,string>>')) return_table as one_return
) t ;


CREATE TABLE temp_white_list_stp11_last_house_condition AS SELECT transport_id,house_condition,
    CASE house_condition
        WHEN '4' THEN 38
        WHEN '' THEN 38
        WHEN '1' THEN 34
         WHEN 'null' THEN 34
        WHEN '0' THEN 29
        WHEN '3' THEN 19
        WHEN '5' THEN 19
        ELSE 0
    END AS last_house_condition FROM
    temp_white_list_stp10;


CREATE TABLE temp_white_list_stp11_last_max_diploma AS SELECT transport_id,
    max_diploma2,
    CASE max_diploma2
        WHEN '1' THEN 24
        WHEN '6' THEN 24
        WHEN '9' THEN 24
        WHEN '2' THEN 29
        WHEN '' THEN 29
        WHEN '3' THEN 52
        WHEN '4' THEN 52
        WHEN '5' THEN 52
        WHEN '8' THEN 52
        ELSE 0
    END AS last_max_diploma FROM
    temp_white_list_stp10;



create table  temp_white_list_stp11_delay_per_overdue_term_1 as SELECT transport_id,
    SUM(CASE
        WHEN
            (acctflag = '1' AND delayflag != 'true'
                AND repayownbdate < FROM_UNIXTIME(UNIX_TIMESTAMP(), 'yyyy-MM-dd'))
                OR repayownbdate >= FROM_UNIXTIME(UNIX_TIMESTAMP(), 'yyyy-MM-dd')
        THEN
            0
        WHEN
            acctflag = '1' AND delayflag = 'true'
                AND termretdate < FROM_UNIXTIME(UNIX_TIMESTAMP(), 'yyyy-MM-dd')
                AND repayownbdate < FROM_UNIXTIME(UNIX_TIMESTAMP(), 'yyyy-MM-dd')
        THEN
            datediff(termretdate , repayownbdate)
        ELSE datediff(FROM_UNIXTIME(UNIX_TIMESTAMP(), 'yyyy-MM-dd') ,repayownbdate)
    END) AS sum_delay,
    SUM(CASE
        WHEN
            (acctflag = '1' AND delayflag != 'true'
                AND repayownbdate < FROM_UNIXTIME(UNIX_TIMESTAMP(), 'yyyy-MM-dd'))
                OR repayownbdate >= FROM_UNIXTIME(UNIX_TIMESTAMP(), 'yyyy-MM-dd')
        THEN
            0
        ELSE 1
    END) AS overdue_term
FROM
    temp_white_list_stp11
GROUP BY transport_id;








CREATE TABLE temp_white_list_stp11_delay_per_overdue_term_2 AS SELECT a.*,
(a.sum_delay / a.overdue_term) AS delay_per_overdue_term FROM
temp_white_list_stp11_delay_per_overdue_term_1 a;


CREATE TABLE temp_white_list_stp11_delay_per_overdue_term_3 AS SELECT a.*,
CASE
WHEN a.delay_per_overdue_term< 1.001  THEN 36
WHEN a.delay_per_overdue_term is NULL THEN 36
WHEN a.delay_per_overdue_term>=1.001  and  a.delay_per_overdue_term< 2 THEN 26
WHEN a.delay_per_overdue_term>=2 THEN 20
ELSE 0
END AS delay_per_overdue_term_score FROM
temp_white_list_stp11_delay_per_overdue_term_2  a;






CREATE TABLE temp_white_list_stp11_unpaid_prin_rate_1 AS
    SELECT
        a.*, b.paid_prin
    FROM
        (SELECT
             transport_id, contractamt, settledate
         FROM
             temp_white_list_stp10) a,
        (SELECT
             transport_id,
             SUM(CASE
                 WHEN repayownbdate < FROM_UNIXTIME(UNIX_TIMESTAMP(), 'yyyy-MM-dd') THEN termretprin
                 ELSE 0
                 END) AS paid_prin
         FROM
             temp_white_list_stp11
         GROUP BY transport_id) b
    WHERE
        a.transport_id = b.transport_id;




CREATE TABLE temp_white_list_stp11_unpaid_prin_rate_2 AS
    SELECT
        a.*,
        CASE
        WHEN
            settledate < FROM_UNIXTIME(UNIX_TIMESTAMP(), 'yyyy-MM-dd')
            AND settledate != ''
            THEN
                0
        ELSE ( (contractamt - paid_prin) / contractamt)
        END AS unpaid_prin_rate
    FROM
      temp_white_list_stp11_unpaid_prin_rate_1 a;





CREATE TABLE temp_white_list_stp11_unpaid_prin_rate_3 AS SELECT a.*,
CASE
WHEN a.unpaid_prin_rate< 0.001  THEN 32
WHEN a.unpaid_prin_rate is NULL THEN 32
WHEN a.unpaid_prin_rate>=0.001  and  a.unpaid_prin_rate< 0.25 THEN 52
WHEN a.unpaid_prin_rate< 0.5   and  a.unpaid_prin_rate>=0.25 THEN 34
WHEN a.unpaid_prin_rate>=0.5 THEN 17
ELSE 0
END AS unpaid_prin_rate_score FROM
temp_white_list_stp11_unpaid_prin_rate_2  a;



CREATE  TABLE  temp_white_list_stp12_score_1 AS
select transport_id,last_house_condition,'last_house_condition' as flag from temp_white_list_stp11_last_house_condition
union all
select transport_id,last_max_diploma,'last_max_diploma' as flag from temp_white_list_stp11_last_max_diploma
union all
select transport_id,delay_per_overdue_term_score,'delay_per_overdue_term_score' as flag  from temp_white_list_stp11_delay_per_overdue_term_3
union all
select transport_id,unpaid_prin_rate_score ,'unpaid_prin_rate_score' as flag from temp_white_list_stp11_unpaid_prin_rate_3;



CREATE  TABLE  temp_white_list_stp12_score_2 AS
select transport_id,sum(last_house_condition) AS score
from temp_white_list_stp12_score_1
group by transport_id;



CREATE TABLE temp_white_list_stp12_score_3 AS SELECT a.*,
CASE
WHEN a.score< 85  THEN 20
WHEN a.score>=85 and  a.score < 90 THEN 19
WHEN a.score>=90 and  a.score < 95 THEN 18
WHEN a.score>=95 and  a.score < 100 THEN 17
WHEN a.score>=100 and  a.score < 105 THEN 16
WHEN a.score>=105 and  a.score < 110 THEN 15
WHEN a.score>=110 and  a.score < 115 THEN 14
WHEN a.score>=115 and  a.score < 120 THEN 13
WHEN a.score>=120 and  a.score < 125 THEN 12
WHEN a.score>=125 and  a.score < 130 THEN 11
WHEN a.score>=130 and  a.score < 135 THEN 10
WHEN a.score>=135 and  a.score < 140 THEN 9
WHEN a.score>=140 and  a.score < 145 THEN 8
WHEN a.score>=145 and  a.score < 150 THEN 7
WHEN a.score>=150 and  a.score < 155 THEN 6
WHEN a.score>=155 and  a.score < 160 THEN 5
WHEN a.score>=160 and  a.score < 165 THEN 4
WHEN a.score>=165 and  a.score < 170 THEN 3
WHEN a.score>=170 and  a.score < 175 THEN 2
WHEN a.score>=175  THEN 1
ELSE 0
END AS level FROM
temp_white_list_stp12_score_2  a;





CREATE TABLE temp_white_list_stp12 AS SELECT a.*, b.score, b.level FROM
    temp_white_list_stp10 a
    LEFT JOIN
    temp_white_list_stp12_score_3 b ON a.transport_id = b.transport_id;







insert overwrite directory '/user/yisou/jiajincao/white_list_in'
select  distinct
birthday	,
uuid	,
source	,
transport_id	,
name	,
user_id	,
temp_white_list_stp12.id_number	,
mobile	,
mobile2	,
apply_time	,
apply_device_id	,
apply_id	,
apply_ip	,
apply_department_name	,
apply_department_city	,
apply_latitude	,
apply_longitude	,
bank_card_num	,
bank_name	,
invite_code	,
invite_code_data	,
invite_mobile	,
is_expand	,
amortisation	,
product_type	,
loan_purpose	,
loan_type	,
register_time	,
register_city	,
register_detail_address	,
register_latitude	,
register_longitude	,
register_province	,
register_device_id	,
register_ip	,
resident_duration	,
resident_city	,
resident_detail_address	,
resident_district	,
resident_province	,
resident_area_code	,
resident_full_number	,
resident_number	,
resident_status	,
sales_person_name	,
sfz_edit_count	,
sfz_error_count	,
org_name	,
org_detail_address	,
org_provice	,
org_city	,
org_district	,
org_area_code	,
org_full_number	,
org_number	,
occupation	,
salary	,
credit_card_or_load	,
domicile_city	,
domicile_detail_address	,
domicile_district	,
domicile_provice	,
email	,
house_city	,
house_detail_address	,
house_district	,
house_province	,
marriage	,
max_diploma	,
qq	,
social_insurance	,
total_amount	,
process_status	,
borrow_amount	,
borrow_status	,
customerid ,
contract_id	,
end_date	,
decision_desc	,
smp_office_id   ,
decision_inhand_amount	,
decision_amount	,
decision_month_return	,
decision_loan_term	,
cashier_time	,
month_return	,
paid_amount	,
refuse_code	,
repay_time	,
complete_type	,
return_list	,
current_overdue_days	,
current_term_expect_amount	,
last_term_status	,
max_overdue_days	,
owed_contract_amount	,
owed_contract_corpus	,
recent_12_terms	,
recent_24_terms	,
returned_terms	,
total_overdue_count	,
total_overdue_days	,
contacts	,
account_source	,
issueamt	,
house_status	,
has_car	,
credit_level	,
prepay, settledate,feeflag,score,level  from
temp_white_list_stp12
left  join
(select distinct id_number  from mortgagor_$yesterday where source like '%jhjj%'
and  process_status not like '%已结清%'
union all
select distinct id_number from  mortgagor_$yesterday where source like '%jhjj%'
and  total_overdue_days > 0 ) tt2
on (temp_white_list_stp12.id_number = tt2.id_number)
where tt2.id_number is null;


"

version=`date +%Y%m%d%H%M`


mv white_list_out.csv pre_white_list_out_"$version".csv
mv white_list_fail.txt pre_white_list_fail_"$version".txt

/home/yisou/anaconda2/bin/python2.7 white_list.py
