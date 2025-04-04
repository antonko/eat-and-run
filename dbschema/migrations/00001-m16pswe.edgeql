CREATE MIGRATION m16pswepwgttj35r24w42olduwbfovqxmg53juv4geq2bwbsiuchba
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
};
