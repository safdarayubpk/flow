// Dynamic route for viewing/editing a single task
// This is a placeholder as Next.js 16+ App Router handles dynamic routes differently
// In a real implementation, this would be handled by the main tasks page with client-side navigation

export default function SingleTaskPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">Task Details</h1>
        </div>
      </header>
      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="bg-white shadow rounded-lg p-6">
              <div className="text-center py-8">
                <p className="text-gray-500">Task details view</p>
                <p className="text-sm text-gray-400 mt-2">This page is accessible via client-side navigation from the task list</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}