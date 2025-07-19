$(document).ready(function () {
    var chatStarted = false;
    // typing flag removed – we will not block user input while the bot is typing
    var currentTypingEffect;
    var currentBotResponse;

    $('form').on('submit', function (event) {
        event.preventDefault();
        var messageInput = $('#userInput');
        var chatlogContainer = $('#chatlog');
        var userMessage = messageInput.val().trim();

        // Allow sending even while the bot is typing its previous reply.
        if (userMessage === '') {
            return;
        }


        messageInput.val(''); // leave the input enabled for the next command

        var userMessageHtml = `<div class="msg right-msg"><div class="msg-bubble"><div class="msg-text"><strong>You:</strong> ${userMessage}</div></div></div>`;
        chatlogContainer.append(userMessageHtml);

        if (!chatStarted) {
            $('.no-chat').addClass('d-none');
            $('.main-chat').css('background-color', '#0a0e17');
            $('.chat-header').css('background-color', '#0a0e17');
            chatStarted = true;
        }
        
        var typingElement = chatlogContainer.find('.typing-animation');
        typingElement.closest('.msg.left-msg').remove();
        chatlogContainer.append(`<div class="msg left-msg"><div class="msg-bubble botchat">${typingAnimation()}</div></div>`);

        $.ajax({
            type: 'POST',
            url: '/chat/',
            data: {
                message: userMessage,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function (data) {
                console.log(data);
                var typingElement = chatlogContainer.find('.typing-animation');

                typingElement.closest('.msg.left-msg').remove();

                if (data.bot_response) {
                    var botResponse = $('<div class="msg left-msg"><div class="msg-bubble botchat"><p><strong>LouBot:</strong> <span class="typewriter"></span></p><button class="gg-play-button-o"></button></div></div>');
                    chatlogContainer.append(botResponse);
                    currentBotResponse = botResponse.find('.typewriter');

                    currentTypingEffect = typeWriter(currentBotResponse, data.bot_response, function () {
                        chatlogContainer.animate({ scrollTop: chatlogContainer[0].scrollHeight });
                        // typing finished – remove play button
                        botResponse.find('.gg-play-button-o').remove();
                    });

                    botResponse.find('.gg-play-button-o').on('click', function () {
                        clearInterval(currentTypingEffect);
                        $(this).remove();
                    });
                }
            },
            error: function (xhr, status, error) {
                console.error(xhr.responseText);
            },
            beforeSend: function () {}
        });
    });

    function typeWriter(element, text, callback) {
        var i = 0;
        // speed up typing to 25 ms per character for snappier UI
        return setInterval(function () {
            if (i < text.length) {
                element.text(element.text() + text.charAt(i));
                i++;
            } else {
                clearInterval(currentTypingEffect);
                if (callback) callback();
            }
        }, 25);
    }

    function toggleDots() {
        var dots = $('.dots');
        dots.text(dots.text() + '.');
        if (dots.text().length > 5) {
            dots.text('');
        }
    }

    setInterval(toggleDots, 300);
});

function typingAnimation() {
    return `<p><strong>LouBot:</strong> 
            <span class="typing-animation"></span>
            <span class="typing-animation"></span>
            <span class="typing-animation"></span></p>`;
}


// Utils
function get(selector, root = document) {
    return root.querySelector(selector);
}

function formatDate(date) {
    const h = "0" + date.getHours();
    const m = "0" + date.getMinutes();

    return `${h.slice(-2)}:${m.slice(-2)}`;
}

function random(min, max) {
    return Math.floor(Math.random() * (max - min) + min);
}