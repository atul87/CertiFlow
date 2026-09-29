export default function Loading() {
  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-screen-xl mx-auto animate-pulse">
      {/* Page header skeleton */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-2">
          <div className="h-7 w-48 bg-gray-100 rounded-xl" />
          <div className="h-4 w-72 bg-gray-100 rounded-lg" />
        </div>
        <div className="flex gap-2">
          <div className="h-9 w-24 bg-gray-100 rounded-xl" />
          <div className="h-9 w-32 bg-[var(--color-primary)]/10 rounded-xl" />
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="bg-white rounded-2xl border border-[var(--color-border)] p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div className="h-3 w-20 bg-gray-100 rounded-lg" />
              <div className="w-8 h-8 bg-gray-100 rounded-xl" />
            </div>
            <div className="h-8 w-24 bg-gray-100 rounded-xl" />
            <div className="h-3 w-32 bg-gray-100 rounded-lg" />
          </div>
        ))}
      </div>

      {/* Main content card */}
      <div className="bg-white rounded-2xl border border-[var(--color-border)] overflow-hidden">
        <div className="px-5 py-4 border-b border-[var(--color-border)] flex items-center justify-between">
          <div className="h-5 w-32 bg-gray-100 rounded-lg" />
          <div className="h-4 w-16 bg-gray-100 rounded-lg" />
        </div>
        {/* Table rows */}
        {[1, 2, 3, 4, 5, 6].map(i => (
          <div key={i} className="px-5 py-4 border-b border-[var(--color-border)] flex items-center gap-4">
            <div className="w-8 h-8 bg-gray-100 rounded-full shrink-0" />
            <div className="flex-1 space-y-1.5">
              <div className="h-4 w-48 bg-gray-100 rounded-lg" />
              <div className="h-3 w-32 bg-gray-100 rounded-md" />
            </div>
            <div className="h-5 w-16 bg-gray-100 rounded-full" />
            <div className="h-4 w-12 bg-gray-100 rounded-lg" />
          </div>
        ))}
      </div>
    </div>
  );
}
