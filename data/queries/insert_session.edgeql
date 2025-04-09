with 
    chat_id := <str>$chat_id,
    messages := <json>$messages

select (
    insert Session {
        chat_id := chat_id,
        messages := messages
    }
) {
    id,
    chat_id,
    messages,
    created_at
}; 