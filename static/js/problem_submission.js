ToolTip.init({
    delay: 400,
    fadeDuration: 250,
    fontSize: '1.0em',
    theme: 'light',
    textColor: '#757575',
    shadowColor: '#000',
    fontFamily: "'Roboto-Medium', 'Roboto-Regular', Arial",
    trigger:"a",
    position:"LEFT"
});

var fl = setInterval(function(){
    var flag = false;
    var no = new Array();
    var cnt = 0;
    $('table tr').each(function() {
    var text = $(this).children().eq(5).children("span").text();
        if(text != "评测完成" && text != "提交成功" && text != "编译错误"  && text != "系统错误" && text != "评测状态"){
            no[cnt]=$(this);
            flag = true;
            cnt++;
        }
    })
    if(cnt > 0){
        var url = $("#problem_submission").attr("value");
        $.ajax({
            url: url,
            type:'GET',
            data:{
                "cnt": cnt
            },
            success : function(submission_list) {
                var index = 0;
                $(submission_list).each (
                    function() {
                        if (index < cnt) {
                            var status_message = this.status_message;
                            no[index].children().eq(5).children("span").attr("data-tip",status_message)

                            if(this.status == -3) {
                                no[index].children().eq(5).css("color","#A4CACA");
                                no[index].children().eq(5).children("span").text("提交成功");
                            }
                            else if (this.status == -2) {
                                no[index].children().eq(5).css("color","#A4CACA");
                                no[index].children().eq(5).children("span").text("队列中");
                            }

                            else if (this.status == -1) {
                                no[index].children().eq(5).css("color","#A4CACA");
                                no[index].children().eq(5).children("span").text(this.running_process);
                            }
                            else if (this.status == 0) {
                                no[index].children().eq(5).css("color","#009A08");
                                no[index].children().eq(5).children("div").remove()
                                no[index].children().eq(5).children("span").text("评测完成");
                            }
                            else if (this.status == 2) {
                                no[index].children().eq(5).css("color","#FF8C00");
                                no[index].children().eq(5).children("div").remove()
                                no[index].children().eq(5).children("span").text("编译错误");
                            }
                            else if (this.status == 3) {
                                no[index].children().eq(5).css("color","#FF0A32");
                                no[index].children().eq(5).children("div").remove()
                                no[index].children().eq(5).children("span").text("系统错误");
                            }
                            if(this.status_percent == 100) {
                                no[index].children().eq(6).css("color","#009A08");
                                no[index].children().eq(6).text(this.status_percent.toFixed(1));
                            }
                            else if(this.status_percent > 0) {
                                no[index].children().eq(6).css("color","#FF8C00");
                                no[index].children().eq(6).text(this.status_percent.toFixed(1));
                            }
                            else {
                                no[index].children().eq(6).css("color","#FF0A32");
                                no[index].children().eq(6).text(this.status_percent.toFixed(1));
                            }
                            if(this.status >= 0){
                                var arr=new Array();
                                var ar=new Array();
                                var time;
                                time=this.judge_end_time.toString();
                                arr=time.split('.');
                                ar=arr[0].split('T');
                                no[index].children().eq(2).text(ar[0]+" "+ar[1]);
                            }
                        }
                        index++;
                    }
                )
            }
        })
    }

    if(flag == false){
        window.clearInterval(fl);
    }
},2000);
// 作者认为这个数很吉利