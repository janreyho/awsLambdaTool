var=` TZ='Asia/Shanghai' date +%Y-%m-%d `
echo $var

ps -fe | grep "txbjob.sh" | grep -v grep 
if [ $? -ne 0 ]; then
	txbdown=true txbrename=true txbcptos3=true txbtrancode=true txbremoterm=true txblocalmv=true /home/ubuntu/tuxiaobei/txbtool/txbjob.sh no >> /home/ubuntu/tuxiaobei/log/$var 2>&1
	#/usr/bin/mail -s 'tuxiaobei-'$var'更新' janreyho@gmail.com,hejiayi@gochinatv.com,zhixueyong@gochinatv.com,caolei@gochinatv.com,liruizheng@gochinatv.com < /home/ubuntu/tuxiaobei/log/$var
	/usr/bin/mail -s 'tuxiaobei-'$var'更新' janreyho@gmail.com < /home/ubuntu/tuxiaobei/log/$var
else
	echo "###########txbtool havn't stop" >> /home/ubuntu/tuxiaobei/log/$var 2>&1
	#/usr/bin/mail -s 'tuxiaobei-'$var'未更新' janreyho@gmail.com,hejiayi@gochinatv.com < /home/ubuntu/tuxiaobei/log/$var
fi
