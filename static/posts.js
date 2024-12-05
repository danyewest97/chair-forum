$(document).ready(function() {
	
	$("textarea.card-text").each(function() {
		var newText = "";
		var oldText = $(this).text();
		
		if (oldText.length > 10) {
			newText = oldText.substring(0, 10);
			newText += "..."
			
			$(this).text(newText);
			$(this).data("is-cutoff", "true");
		}
		
	});
});