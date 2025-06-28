class DuneSQLQueryBuilder:
    """Builds and composes SQL for DuneQuery."""

    def build_filters(self) -> str:
        """Return the SQL WHERE clause for included filters."""
        if not self.filters:
            return ""
        clauses = [f"{k} = '{v}'" for k, v in self.filters.items()]
        return "WHERE " + " AND ".join(clauses)

    def build_exclude(self) -> str:
        """Return the SQL WHERE NOT clause for excluded filters."""
        if not self.exclude_filters:
            return ""
        clauses = [f"{k} = '{v}'" for k, v in self.exclude_filters.items()]
        return "WHERE NOT (" + " AND ".join(clauses) + ")"

    def build(self) -> str:
        """Compose the full SQL query string."""
        fields = ", ".join(self.fields) if self.fields else "*"
        sql = f"SELECT {fields} FROM {self.table_name} "
        # apply filters and exclude (mutually exclusive)
        if self.filters:
            sql += self.build_filters() + " "
        elif self.exclude_filters:
            sql += self.build_exclude() + " "
        # ordering
        if getattr(self, "sort_by", None):
            sql += f"ORDER BY {self.sort_by} {self.sort_order} "
        # limit
        if getattr(self, "_limit", 0):
            sql += f"LIMIT {self._limit}"
        return sql.strip()

    def process_query(self):
        """Finalize or execute the SQL based on read-only flag."""
        self.query = self.build()
        if self.is_read_only:
            return type(self)(
                table_name=self.table_name,
                is_read_only=self.is_read_only,
                query=self.query,
                fields=self.fields,
                filters=self.filters,
                exclude_filters=self.exclude_filters,
                limit=self._limit,
                sort_by=self.sort_by,
                sort_order=self.sort_order,
                is_private=self.is_private,
                query_name=self.query_name,
                query_description=self.query_description,
                API_KEY=self.API_KEY,
            )
        return self.execute()