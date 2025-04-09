CREATE MIGRATION m1mmqxmj75at2ntxb6vqglypcosrc7evqx34qhpdugmeynrboc2etq
    ONTO initial
{
  CREATE FUTURE simple_scoping;
  CREATE TYPE default::Meal {
      CREATE REQUIRED PROPERTY calories: std::int64;
      CREATE REQUIRED PROPERTY carbs: std::float64;
      CREATE REQUIRED PROPERTY date: std::datetime;
      CREATE REQUIRED PROPERTY fats: std::float64;
      CREATE REQUIRED PROPERTY name: std::str;
      CREATE REQUIRED PROPERTY proteins: std::float64;
  };
  CREATE TYPE default::Session {
      CREATE REQUIRED PROPERTY chat_id: std::str;
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
      };
      CREATE REQUIRED PROPERTY messages: std::json;
      CREATE PROPERTY updated_at: std::datetime;
  };
};
