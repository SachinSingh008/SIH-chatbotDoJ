$(document).ready(function() {
    $('#chat-button').click(openChat);
    $('#send-button').click(sendMessage);
    $('#user-message').keypress(function(e) {
        if (e.which == 13) {
            sendMessage();
            return false;
        }
    });
    $('#clear-chat').click(clearChat);
    $('#voice-button').click(startVoiceInput);
    $('#back-button').click(closeChat);
    var isFirstMessage = true;
    
    function sendMessage() {
        var userInput = $('#user-message').val().trim();
        var language = $('#language-select').val();
        
        if (userInput === '') return;

        displayUserMessage(userInput);
        $('#user-message').val('');

        showThinking();

        $.ajax({
            url: '/get_response',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 
                message: userInput, 
                language: language,
                is_first_message: isFirstMessage
            }),
            success: function(data) {
                hideThinking();
                if (data.error) {
                    displayBotMessage("I apologize, but I encountered an error: " + data.error + ". Please try again or contact support if the issue persists.", userInput);
                } else {
                    displayBotMessage(data.response, userInput);
                }
                isFirstMessage = false;
            },
            error: function(jqXHR, textStatus, errorThrown) {
                hideThinking();
                console.error("AJAX error: " + textStatus + ' : ' + errorThrown);
                displayBotMessage("I'm having trouble connecting to the server. Please check your internet connection and try again. If the problem persists, please contact support.", userInput);
            }
        });
    }
});
var isFirstMessage = true;


function openChat() {
    $('#chat-container').show();
    $('#chat-button').hide();
    
    if ($('#chatbox').is(':empty')) {
        displayBotMessage("Hi, I am Vaani. How may I help you?");
    }
}

function closeChat() {
    $('#chat-container').hide();
    $('#chat-button').show();
}

function sendMessage() {
    var userInput = $('#user-message').val().trim();
    var language = $('#language-select').val();
    
    if (userInput === '') return;

    displayUserMessage(userInput);
    $('#user-message').val('');

    showThinking();

    // Check if the user is providing a case number
    if (/^\d+$/.test(userInput) && $('.bot-message:last').text().includes("Please provide your case number")) {
        $.ajax({
            url: '/get_case_update',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ case_number: userInput }),
            success: function(data) {
                hideThinking();
                displayBotMessage(data.response, userInput);
            },
            error: function() {
                hideThinking();
                displayBotMessage("Sorry, I'm having trouble retrieving the case information. Please try again later.");
            }
        });
    } else {
        // Existing logic for general queries
        $.ajax({
            url: '/get_response',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ message: userInput, language: language }),
            success: function(data) {
                hideThinking();
                displayBotMessage(data.response, userInput);
            },
            error: function() {
                hideThinking();
                displayBotMessage("Sorry, I'm having trouble connecting to the server. Please try again later.");
            }
        });
    }
}

function displayUserMessage(message) {
    var messageContainer = $('<div class="message-container"></div>');
    messageContainer.append('<div class="message user-message">' + message + '</div>');
    $('#chatbox').append(messageContainer);
    $('#chatbox').scrollTop($('#chatbox')[0].scrollHeight);
}

function displayBotMessage(response, userInput) {
    var messageContainer = $('<div class="message-container"></div>');
    var botMessageContainer = $('<div class="bot-message-container"></div>');
    var botLogo = $('<img class="bot-logo" src="https://cdn-icons-png.flaticon.com/512/4712/4712109.png" alt="bot-logo">');
    var botMessageDiv = $('<div class="message bot-message"></div>');

    botMessageContainer.append(botLogo);
    botMessageContainer.append(botMessageDiv);
    messageContainer.append(botMessageContainer);
    $('#chatbox').append(messageContainer);

    // Split the response into points
    var points = response.split('\n').filter(point => point.trim() !== '');

    function displayNextPoint(index) {
        if (index < points.length) {
            var pointDiv = $('<div class="bot-point"></div>');
            botMessageDiv.append(pointDiv);

            var currentPoint = points[index].replace(/^\s*[\*\-]\s*/, ''); // Remove leading asterisks or hyphens
            var pointText = (index + 1) + '. ' + currentPoint;

            var charIndex = 0;

            function displayNextCharacter() {
                if (charIndex < pointText.length) {
                    pointDiv.append(pointText[charIndex]);
                    
                    // Only auto-scroll if the user hasn't scrolled up
                    var chatbox = $('#chatbox')[0];
                    if (chatbox.scrollHeight - chatbox.scrollTop === chatbox.clientHeight) {
                        chatbox.scrollTop = chatbox.scrollHeight;
                    }
                    
                    charIndex++;
                    setTimeout(displayNextCharacter, 30);
                } else {
                    addDetailLink(pointDiv, currentPoint);
                    setTimeout(() => displayNextPoint(index + 1), 500);
                }
            }

            displayNextCharacter();
        } else {
            addSuggestions(botMessageDiv);
        }
    }

    displayNextPoint(0);
}

function addDetailLink(pointDiv, originalMessage) {
    var detailLink = $('<a href="#" class="detail-link">More Details</a>');
    pointDiv.append(' ');
    pointDiv.append(detailLink);

    detailLink.click(function(e) {
        e.preventDefault();
        requestMoreDetails(originalMessage);
    });
}

function requestMoreDetails(originalMessage) {
    showThinking();

    $.ajax({
        url: '/get_details',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ message: originalMessage }),
        success: function(data) {
            hideThinking();
            displayBotMessage(data.response, originalMessage);
        },
        error: function() {
            hideThinking();
            displayBotMessage("Sorry, I couldn't fetch more details at the moment. Please try again later.");
        }
    });
}

function showThinking() {
    var thinkingHtml = '<div class="thinking"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>';
    $('#chatbox').append(thinkingHtml);
    $('#chatbox').scrollTop($('#chatbox')[0].scrollHeight);
}

function hideThinking() {
    $('.thinking').remove();
}

function addSuggestions(messageDiv) {
    var suggestions = ['What are my court case updates?', 'How do I apply for legal aid?', 'Show me recent amendments.'];
    var suggestionsHtml = '<div class="suggestions">';
    
    suggestions.forEach(function(suggestion) {
        suggestionsHtml += '<button class="suggestion-button">' + suggestion + '</button>';
    });
    
    suggestionsHtml += '</div>';
    messageDiv.append(suggestionsHtml);

    $('.suggestion-button').click(function() {
        var suggestion = $(this).text();
        $('#user-message').val(suggestion);
        sendMessage();
    });

    $('#chatbox').scrollTop($('#chatbox')[0].scrollHeight);
}

function startVoiceInput() {
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'en-IN';
        recognition.start();
        
        recognition.onresult = function(event) {
            var transcript = event.results[0][0].transcript;
            $('#user-message').val(transcript);
            sendMessage();
        };
    } else {
        alert("Sorry, your browser doesn't support speech recognition. Please try using a modern browser like Chrome.");
    }
}

function clearChat() {
    $('#chatbox').empty();
    displayBotMessage("Chat cleared. How else can I assist you?");
}