class DuneSQLQueryBuilder:
    """Builds and composes SQL for DuneQuery."""

    def _build_conditional_clause(self, filters: dict, negate: bool = False) -> str:
        """Return a SQL WHERE clause or WHERE NOT clause based on filters."""
        if not filters:
            return ""
        # reuse lookup logic
        op_map = {
            'gt': '>',
            'lt': '<',
            'gte': '>=',
            'lte': '<=',
            'neq': '!=',
            'in': 'IN',
            'contains': 'LIKE'
        }
        clauses = []
        for key, value in filters.items():
            parts = key.split("__", 1)
            field = parts[0]
            if len(parts) == 1:
                clauses.append(f"{field} = '{value}'")
            else:
                lookup = parts[1]
                sql_op = op_map.get(lookup, '=')
                if lookup == 'in' and isinstance(value, (list, tuple)):
                    vals = ", ".join(f"'{v}'" for v in value)
                    clauses.append(f"{field} IN ({vals})")
                elif lookup == 'contains':
                    clauses.append(f"{field} LIKE '%{value}%'")
                else:
                    clauses.append(f"{field} {sql_op} '{value}'")
        connector = " AND ".join(clauses)
        if negate:
            return f"WHERE NOT ({connector})"
        return f"WHERE {connector}"

    def build_filters(self) -> str:
        """Return the SQL WHERE clause for included filters, supporting lookups like col__gt."""
        return self._build_conditional_clause(self.filters, negate=False)

    def build_exclude(self) -> str:
        """Return the SQL WHERE NOT clause for excluded filters."""
        return self._build_conditional_clause(self.exclude_filters, negate=True)

    def build(self) -> str:
        """Compose the full SQL query string."""
        fields = ", ".join(self.fields) if self.fields else "*"
        sql = f"SELECT {fields} FROM {self.table_name} "

        if self.filters:
            sql += self.build_filters() + " "

        if self.exclude_filters:
            sql += self.build_exclude() + " "

        # ordering
        if getattr(self, "sort_by", None):
            sql += f"ORDER BY {self.sort_by} {self.sort_order} "
        # limit
        if getattr(self, "_limit", 0):
            sql += f"LIMIT {self._limit}"
        return sql.strip()

    def process(self):
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
        return self.execute_all()