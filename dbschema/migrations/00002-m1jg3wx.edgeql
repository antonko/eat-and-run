CREATE MIGRATION m1jg3wxvzjcltt7q7jqlrzzbhsrrpbtr4rtr7de3fkuhnqoer4ogla
    ONTO m16pswepwgttj35r24w42olduwbfovqxmg53juv4geq2bwbsiuchba
{
  CREATE TYPE default::Session {
      CREATE REQUIRED PROPERTY chat_id: std::str;
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
      };
      CREATE REQUIRED PROPERTY messages: std::json;
      CREATE PROPERTY updated_at: std::datetime;
  };
};
