$(document).ready(function() {
   $(".paste").click(function() {
   		form  = $(this).parent().find(".form_paste");
   		form.submit();
   		}
  		
  	)
   $(".paste").each(function() {
   		form  = $(this).parent().find(".form_paste")
		$.data(this, 'action', form.attr("action")
			)
			
   		}
   	)
   	
   $(".cut").click(function() {
   	
   	target_id = $(this).closest('tr').attr('id').split('_')
   	target_id =  target_id[1]
   	
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