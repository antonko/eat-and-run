select Session {
    id,
    chat_id,
    messages,
    created_at,
    updated_at
}
filter .chat_id = <str>$chat_id
limit 1; 