
# 创建用户
CREATE USER 'xwd'@'%' IDENTIFIED BY 'xwd';

# 创建数据库
CREATE DATABASE dianying;
# 把数据库dianying授权给用户xwd
GRANT ALL PRIVILEGES ON dianying.* TO 'xwd'@'%' WITH GRANT OPTION;
# 刷新权限
FLUSH PRIVILEGES;


# 建表
CREATE TABLE IF NOT EXISTS `dianying`(
   `dianying_id` INT UNSIGNED AUTO_INCREMENT,
   `dianying_title` VARCHAR(300) NOT NULL,
   `dianying_url` VARCHAR(300) NOT NULL,
   `dianying_magnet` VARCHAR(500) NOT NULL,
   PRIMARY KEY ( `dianying_id` )
)ENGINE=InnoDB DEFAULT CHARSET=utf8;