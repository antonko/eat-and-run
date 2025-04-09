with 
    chat_id := <str>$chat_id,
    messages := <json>$messages

select (
    update Session 
    filter .chat_id = chat_id
    set {
        messages := messages,
        updated_at := datetime_current()
    }
) {
    id,
    chat_id,
    messages,
    updated_at
}; 