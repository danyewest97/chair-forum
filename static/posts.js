$(document).ready(function() {
	$(".post-body").data("is-cutoff", "false");
	
	var maxCutoffCharacters = 238;
	
	
	$(".post-body").each(function() {
		var body = $(this).children("textarea.card-text");
		
		// Auto-resizes the textareas in the posts so that all the text in each post is shown (up to the maxCutoffCharacters character limit)
		body.on("input", function() {
			this.style.height = "auto";
			this.style.height = this.scrollHeight + "px";
		});
		body.trigger("input");
		
		
		var cutoffText = "";
		var fullText = body.text();
		
		if (fullText.length > maxCutoffCharacters) {
			cutoffText = fullText.substring(0, maxCutoffCharacters);
			cutoffText += "..."
			
			body.text(cutoffText);
			$(this).data("is-cutoff", "true");
			$(this).children("button.show-more-button").css("visibility", "visible");
			
			// Auto-resizes the textareas in the posts so that all the text in each post is shown (up to the maxCutoffCharacters character limit)
			// Doing this a second time here to update the sizes of the posts that exceeded the character limit before storing their cutoff height
			body.on("input", function() {
				this.style.height = "auto";
				this.style.height = this.scrollHeight + "px";
			});
			body.trigger("input");
			
			body.data("full-text", fullText);
			body.data("cutoff-text", cutoffText);
			body.data("cutoff-height", body.height());
		}
		
		
	});
	
	
	
	
	
	$("button.show-more-button").click(function() {
		var parentDiv = $(this).parent();
		var body = parentDiv.children("textarea.card-text");
		
		var fullText = body.data("full-text");
		var cutoffText = body.data("cutoff-text");
		var cutoffHeight = body.data("cutoff-height");
		
		if (parentDiv.data("is-cutoff") === "true") {
			$(this).text("Show Less");
			parentDiv.data("is-cutoff", "false");
			
			body.text(fullText);
			
			
			body.on("input", function() {
				this.style.height = "auto";
				this.style.height = this.scrollHeight + "px";
			});
			body.trigger("input");
			
			parentDiv.css("margin-bottom", "10px");
			
		} else {
			$(this).text("Show More");
			parentDiv.data("is-cutoff", "true");
			
			body.text(cutoffText);
			
			
			body.on("input", function() {
				body.css("height", (cutoffHeight + 4) + "px"); // Adding 4 because JQuery takes 4 pixels off height when using element.height() (idk why)
			});
			body.trigger("input");
			
			
			parentDiv.css("margin-bottom", "0px");
		}
	});
});