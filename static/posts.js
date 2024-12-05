$(document).ready(function() {
	$(".post-body").data("is-cutoff", "false");
	
	$(".post-body").each(function() {
		var body = $(this).children("textarea.card-text");
		
		var cutoffText = "";
		var fullText = body.text();
		
		if (fullText.length > 10) {
			cutoffText = fullText.substring(0, 10);
			cutoffText += "..."
			
			body.text(cutoffText);
			$(this).data("is-cutoff", "true");
			$(this).children("button.show-more-button").css("visibility", "visible");
			body.data("full-text", fullText);
			body.data("cutoff-text", cutoffText);
		}
		
	});
	
	$("button.show-more-button").click(function() {
		var parentDiv = $(this).parent();
		var body = parentDiv.children("textarea.card-text");
		
		var fullText = body.data("full-text");
		var cutoffText = body.data("cutoff-text");
		
		
		if (parentDiv.data("is-cutoff") === "true") {
			$(this).text("Show Less");
			parentDiv.data("is-cutoff", "false");
			
			body.text(fullText);
		} else {
			$(this).text("Show More");
			parentDiv.data("is-cutoff", "true");
			
			body.text(cutoffText);
		}
	});
});