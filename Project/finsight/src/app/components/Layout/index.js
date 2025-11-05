"use client";

import React from "react";
import styles from "./Layout.module.css";

export default function Layout({ children }) {
  return (
    <div className={styles.container}>
      <div className={styles.column_middle}>{children}</div>
    </div>
  );
}