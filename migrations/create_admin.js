migrate(
  (db) => {
    if (process.env.PB_ADMIN_USER && process.env.PB_ADMIN_PASS) {
      const admin = new Admin();
      admin.email = process.env.PB_ADMIN_USER || "admin@localhost";
      admin.setPassword(process.env.PB_ADMIN_PASS || "admin");
      return Dao(db).saveAdmin(admin);
    }
  },
  (db) => {
    if (process.env.PB_ADMIN_USER && process.env.PB_ADMIN_PASS) {
      return Dao(db).deleteAdmin(process.env.PB_ADMIN_USER);
    }
  }
);
