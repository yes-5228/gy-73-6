import { Filter, RotateCcw } from "lucide-react";

const STATUS_OPTIONS = [
  { value: "", label: "全部状态" },
  { value: "pending", label: "待抢单" },
  { value: "claimed", label: "已抢单" },
  { value: "assigned", label: "已派单" },
  { value: "in_progress", label: "服务中" },
  { value: "completed", label: "已完成" },
];

const EXCEPTION_OPTIONS = [
  { value: "", label: "全部" },
  { value: "1", label: "有异常" },
  { value: "0", label: "无异常" },
];

export default function OrderFilter({ filters, setFilters, workers, onReset, onExport }) {
  function updateField(field, value) {
    setFilters({ ...filters, [field]: value });
  }

  const serviceAreas = Array.from(new Set(workers.map((w) => w.service_area).filter(Boolean)));

  return (
    <div className="filter-panel">
      <div className="filter-title">
        <Filter size={18} />
        <h4>组合筛选</h4>
      </div>
      <div className="filter-grid">
        <label>
          预约日期（起）
          <input
            type="date"
            value={filters.move_date_from || ""}
            onChange={(e) => updateField("move_date_from", e.target.value)}
          />
        </label>
        <label>
          预约日期（止）
          <input
            type="date"
            value={filters.move_date_to || ""}
            onChange={(e) => updateField("move_date_to", e.target.value)}
          />
        </label>
        <label>
          服务区域
          <select
            value={filters.service_area || ""}
            onChange={(e) => updateField("service_area", e.target.value)}
          >
            <option value="">全部区域</option>
            {serviceAreas.map((area) => (
              <option value={area} key={area}>{area}</option>
            ))}
          </select>
        </label>
        <label>
          师傅
          <select
            value={filters.worker_id || ""}
            onChange={(e) => updateField("worker_id", e.target.value)}
          >
            <option value="">全部师傅</option>
            {workers.map((worker) => (
              <option value={worker.id} key={worker.id}>{worker.name}</option>
            ))}
          </select>
        </label>
        <label>
          状态
          <select
            value={filters.status || ""}
            onChange={(e) => updateField("status", e.target.value)}
          >
            {STATUS_OPTIONS.map((opt) => (
              <option value={opt.value} key={opt.value}>{opt.label}</option>
            ))}
          </select>
        </label>
        <label>
          异常标记
          <select
            value={filters.has_exception || ""}
            onChange={(e) => updateField("has_exception", e.target.value)}
          >
            {EXCEPTION_OPTIONS.map((opt) => (
              <option value={opt.value} key={opt.value}>{opt.label}</option>
            ))}
          </select>
        </label>
      </div>
      <div className="filter-actions">
        <button className="secondary-button" type="button" onClick={onReset}>
          <RotateCcw size={16} />
          重置
        </button>
        <button className="primary-button" type="button" onClick={onExport}>
          导出 CSV
        </button>
      </div>
    </div>
  );
}
