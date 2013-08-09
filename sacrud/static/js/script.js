$(document).ready(function() {
   $(".paste").click(function() {
   		form  = $(this).parent().find(".form_paste");
   		form.submit();
   		}
  	)
   $(".paste").each(function() {
   		form  = $(this).parent().find(".form_paste")
		$.data(this, 'action', form.attr("action"))
   		}
   	)
   	
   $(".cut").click(function() {
   	
   	$('.selected').removeClass("selected")
   	row = $(this).closest('tr')
   	target_id = row.attr('id').split('_').pop()
   	
   	new_row = row.clone()
   	new_row.find('td').last().hide()
   	table = "<table>" + new_row.html() + "</table>"
   	message = "You choose element to move" + table 
   	$("#cutelement").html(message)
   	$("#cutelement").show()
   	row.addClass("selected")
	$("#cutelement").addClass("selected")
	$(".paste").each(function(){
		action = $.data(this, 'action')
		form  = $(this).parent().find(".form_paste")
		action = URI.expand(action+"/{target_id}",
							{ 
							target_id :target_id
							}
							)
		$(this).show()
		form.attr('action', action)
		
	})
   		
   })
 });
