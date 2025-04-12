CREATE MIGRATION m1ekowga2x2gzocojbs2rrvbtggcelntmc7uua5j3jrccng7bckkoq
    ONTO initial
{
  CREATE SCALAR TYPE default::WorkoutType EXTENDING enum<RUNNING, WALKING, CYCLING, SWIMMING, STRENGTH_TRAINING, FLEXIBILITY, TEAM_SPORTS, MARTIAL_ARTS, WINTER_SPORTS, OTHER>;
  CREATE FUTURE simple_scoping;
  CREATE TYPE default::Meal {
      CREATE REQUIRED PROPERTY calories: std::int64;
      CREATE REQUIRED PROPERTY carbs: std::float64;
      CREATE REQUIRED PROPERTY consumed_at: std::datetime;
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
      };
      CREATE REQUIRED PROPERTY fats: std::float64;
      CREATE REQUIRED PROPERTY is_junk_food: std::bool {
          SET default := false;
      };
      CREATE REQUIRED PROPERTY name: std::str;
      CREATE REQUIRED PROPERTY proteins: std::float64;
      CREATE REQUIRED PROPERTY weight: std::float64;
  };
  CREATE TYPE default::Photo {
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
      };
      CREATE PROPERTY description: std::str;
      CREATE REQUIRED PROPERTY file_data: std::bytes;
      CREATE REQUIRED PROPERTY file_name: std::str;
      CREATE REQUIRED PROPERTY mime_type: std::str;
  };
  ALTER TYPE default::Meal {
      CREATE LINK photo: default::Photo;
  };
  CREATE TYPE default::User {
      CREATE MULTI LINK meals: default::Meal {
          ON SOURCE DELETE DELETE TARGET;
      };
      CREATE MULTI LINK photos: default::Photo {
          ON SOURCE DELETE DELETE TARGET;
      };
      CREATE REQUIRED PROPERTY chat_id: std::str {
          CREATE CONSTRAINT std::exclusive;
      };
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
      };
      CREATE PROPERTY interaction_count: std::int64 {
          SET default := 0;
      };
      CREATE PROPERTY last_interaction_date: std::datetime;
      CREATE REQUIRED PROPERTY state: std::json;
  };
  ALTER TYPE default::Meal {
      CREATE LINK user: default::User {
          ON TARGET DELETE DELETE SOURCE;
      };
  };
  CREATE TYPE default::Memory {
      CREATE LINK user: default::User {
          ON TARGET DELETE DELETE SOURCE;
      };
      CREATE REQUIRED PROPERTY content: std::str;
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
      };
      CREATE REQUIRED PROPERTY importance: std::int16 {
          SET default := 1;
      };
      CREATE PROPERTY updated_at: std::datetime;
  };
  ALTER TYPE default::User {
      CREATE MULTI LINK memories: default::Memory {
          ON SOURCE DELETE DELETE TARGET;
      };
  };
  ALTER TYPE default::Photo {
      CREATE LINK user: default::User {
          ON TARGET DELETE DELETE SOURCE;
      };
  };
  CREATE TYPE default::Workout {
      CREATE LINK photo: default::Photo;
      CREATE LINK user: default::User {
          ON TARGET DELETE DELETE SOURCE;
      };
      CREATE REQUIRED PROPERTY calories_burned: std::int64;
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
      };
      CREATE PROPERTY distance_km: std::float64;
      CREATE REQUIRED PROPERTY duration_minutes: std::int32;
      CREATE REQUIRED PROPERTY name: std::str;
      CREATE PROPERTY pace_min_per_km: std::float64;
      CREATE REQUIRED PROPERTY workout_date: std::datetime;
      CREATE REQUIRED PROPERTY workout_type: default::WorkoutType;
  };
  ALTER TYPE default::User {
      CREATE MULTI LINK workouts: default::Workout {
          ON SOURCE DELETE DELETE TARGET;
      };
  };
};
