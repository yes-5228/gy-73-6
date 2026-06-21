import { AlertTriangle, ClipboardList, Truck } from "lucide-react";

import StatusBadge from "../../components/StatusBadge.jsx";
import OrderFilter from "./OrderFilter.jsx";

export default function OrderBoard({
  orders,
  workers,
  onClaim,
  onAssign,
  filters,
  setFilters,
  onResetFilters,
  onExport,
}) {
  return (
    <div className="panel">
      <div className="panel-title">
        <ClipboardList size={20} />
        <h3>订单池与派单</h3>
        <span className="order-count">共 {orders.length} 条</span>
      </div>
      <OrderFilter
        filters={filters}
        setFilters={setFilters}
        workers={workers}
        onReset={onResetFilters}
        onExport={onExport}
      />
      <div className="order-list">
        {orders.map((order) => (
          <article className="order-card" key={order.id}>
            <div className="order-card-head">
              <div>
                <h4>
                  {order.customer_name}
                  {order.has_exception && (
                    <span className="exception-tag" title="异常订单">
                      <AlertTriangle size={14} />
                      异常
                    </span>
                  )}
                </h4>
                <p>
                  {order.move_date} {order.move_time}
                  {order.service_area && <span className="service-area-tag">· {order.service_area}</span>}
                </p>
              </div>
              <StatusBadge status={order.status} label={order.status_label} />
            </div>
            <div className="route">
              <span>{order.origin}</span>
              <Truck size={16} />
              <span>{order.destination}</span>
            </div>
            <p className="muted">物品：{order.items || "未填写"}</p>
            <div className="assignment">
              <span>抢单师傅：{order.claimed_by?.name || "暂无"}</span>
              <span>派单师傅：{order.assigned_to?.name || "暂无"}</span>
            </div>
            <div className="button-row">
              <select
                aria-label="选择抢单师傅"
                defaultValue=""
                onChange={(e) => e.target.value && onClaim(order.id, Number(e.target.value))}
                disabled={order.status !== "pending"}
              >
                <option value="">师傅抢单</option>
                {workers.map((worker) => (
                  <option value={worker.id} key={worker.id}>{worker.name}</option>
                ))}
              </select>
              <select
                aria-label="选择派单师傅"
                defaultValue=""
                onChange={(e) => e.target.value && onAssign(order.id, Number(e.target.value))}
                disabled={order.status === "completed" || order.status === "in_progress"}
              >
                <option value="">平台派单</option>
                {workers.map((worker) => (
                  <option value={worker.id} key={worker.id}>{worker.name}</option>
                ))}
              </select>
            </div>
          </article>
        ))}
        {orders.length === 0 && <p className="empty">暂无符合条件的订单</p>}
      </div>
    </div>
  );
}
