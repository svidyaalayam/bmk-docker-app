import { useMemo, useState, type ReactNode } from 'react'

export type DataTableColumn<T> = {
  key: string
  header: string
  sortable?: boolean
  /** Include this column in the search box (default true when getValue/render text exists). */
  filterable?: boolean
  getValue?: (row: T) => string | number | boolean | null | undefined
  sortValue?: (row: T) => string | number | boolean | null | undefined
  render?: (row: T) => ReactNode
  className?: string
}

type SortDir = 'asc' | 'desc'

type DataTableProps<T> = {
  rows: T[]
  columns: DataTableColumn<T>[]
  rowKey: (row: T) => string | number
  emptyMessage?: string
  initialPageSize?: number
  pageSizeOptions?: number[]
  searchPlaceholder?: string
}

function cellText<T>(row: T, column: DataTableColumn<T>): string {
  if (column.getValue) {
    const value = column.getValue(row)
    if (value == null) return ''
    return String(value)
  }
  return ''
}

function compareValues(a: unknown, b: unknown): number {
  if (a == null && b == null) return 0
  if (a == null) return -1
  if (b == null) return 1
  if (typeof a === 'number' && typeof b === 'number') return a - b
  if (typeof a === 'boolean' && typeof b === 'boolean') return Number(a) - Number(b)
  return String(a).localeCompare(String(b), undefined, { sensitivity: 'base', numeric: true })
}

export default function DataTable<T>({
  rows,
  columns,
  rowKey,
  emptyMessage = 'No rows found.',
  initialPageSize = 10,
  pageSizeOptions = [5, 10, 25, 50],
  searchPlaceholder = 'Filter rows…',
}: DataTableProps<T>) {
  const [query, setQuery] = useState('')
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<SortDir>('asc')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(initialPageSize)

  const filteredSorted = useMemo(() => {
    const q = query.trim().toLowerCase()
    let next = rows

    if (q) {
      next = rows.filter((row) =>
        columns.some((column) => {
          if (column.filterable === false) return false
          const text = cellText(row, column).toLowerCase()
          return text.includes(q)
        }),
      )
    }

    if (sortKey) {
      const column = columns.find((c) => c.key === sortKey)
      if (column) {
        const sorted = [...next].sort((left, right) => {
          const leftValue = column.sortValue
            ? column.sortValue(left)
            : column.getValue
              ? column.getValue(left)
              : ''
          const rightValue = column.sortValue
            ? column.sortValue(right)
            : column.getValue
              ? column.getValue(right)
              : ''
          const result = compareValues(leftValue, rightValue)
          return sortDir === 'asc' ? result : -result
        })
        next = sorted
      }
    }

    return next
  }, [rows, columns, query, sortKey, sortDir])

  const totalPages = Math.max(1, Math.ceil(filteredSorted.length / pageSize))
  const currentPage = Math.min(page, totalPages)
  const pageStart = (currentPage - 1) * pageSize
  const pageRows = filteredSorted.slice(pageStart, pageStart + pageSize)

  const toggleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir((prev) => (prev === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(key)
      setSortDir('asc')
    }
    setPage(1)
  }

  return (
    <div className="data-table">
      <div className="data-table-toolbar">
        <label className="data-table-search">
          <span className="sr-only">Filter</span>
          <input
            type="search"
            value={query}
            placeholder={searchPlaceholder}
            onChange={(e) => {
              setQuery(e.target.value)
              setPage(1)
            }}
          />
        </label>
        <label className="data-table-page-size">
          Rows
          <select
            value={pageSize}
            onChange={(e) => {
              setPageSize(Number(e.target.value))
              setPage(1)
            }}
          >
            {pageSizeOptions.map((size) => (
              <option key={size} value={size}>
                {size}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              {columns.map((column) => {
                const sortable = column.sortable !== false && Boolean(column.getValue || column.sortValue)
                const active = sortKey === column.key
                return (
                  <th key={column.key} className={column.className}>
                    {sortable ? (
                      <button
                        type="button"
                        className={`data-table-sort${active ? ' active' : ''}`}
                        onClick={() => toggleSort(column.key)}
                      >
                        <span>{column.header}</span>
                        <span aria-hidden="true" className="data-table-sort-icon">
                          {active ? (sortDir === 'asc' ? '▲' : '▼') : '↕'}
                        </span>
                      </button>
                    ) : (
                      column.header
                    )}
                  </th>
                )
              })}
            </tr>
          </thead>
          <tbody>
            {pageRows.map((row) => (
              <tr key={rowKey(row)}>
                {columns.map((column) => (
                  <td key={column.key} className={column.className}>
                    {column.render
                      ? column.render(row)
                      : cellText(row, column) || '—'}
                  </td>
                ))}
              </tr>
            ))}
            {pageRows.length === 0 && (
              <tr>
                <td colSpan={columns.length}>{emptyMessage}</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="data-table-footer">
        <p className="data-table-meta">
          {filteredSorted.length === 0
            ? '0 results'
            : `Showing ${pageStart + 1}–${Math.min(pageStart + pageSize, filteredSorted.length)} of ${filteredSorted.length}`}
          {query.trim() ? ` (filtered from ${rows.length})` : ''}
        </p>
        <div className="data-table-pager">
          <button
            type="button"
            className="tab"
            disabled={currentPage <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            Previous
          </button>
          <span>
            Page {currentPage} / {totalPages}
          </span>
          <button
            type="button"
            className="tab"
            disabled={currentPage >= totalPages}
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  )
}
