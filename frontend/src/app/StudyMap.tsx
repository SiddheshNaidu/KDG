import { useEffect, useMemo, useRef } from "react";
import {
  Background,
  Controls,
  Handle,
  MarkerType,
  MiniMap,
  Position,
  ReactFlow,
  ReactFlowProvider,
  useReactFlow,
  type Edge as FlowEdge,
  type FitViewOptions,
  type Node as FlowNode,
} from "@xyflow/react";
import dagre from "@dagrejs/dagre";
import "@xyflow/react/dist/style.css";
import type { Edge, Node, NodeState } from "./api";
import { Check, Star, unitColor } from "./ui";

const W = 208;
const H = 54;
const ROWS_PER_COLUMN = 12; // a long unit wraps into a second column
const COL_GAP = 28;
const UNIT_GAP = 70;
const ROW_GAP = 12;
const HEADER_H = 64;

type Look = "none" | "selected" | "prereq" | "next" | "dim";
type TopicData = { name: string; unit: number; start: boolean; key: boolean; state?: NodeState["state"]; look: Look };
type UnitData = { unit: number; title?: string };

const hidden = { opacity: 0, pointerEvents: "none" as const, width: 1, height: 1 };

function TopicNode({ data }: { data: TopicData }) {
  const cls = ["sm-node", data.state ?? "", data.look !== "none" ? data.look : "", data.key ? "key" : ""].join(" ");
  return (
    <div className={cls} style={{ ["--u" as string]: unitColor(data.unit) }} title={data.name}>
      <Handle id="l" type="target" position={Position.Left} style={hidden} />
      <Handle id="rt" type="target" position={Position.Right} style={hidden} />
      <Handle id="r" type="source" position={Position.Right} style={hidden} />
      <Handle id="lt" type="source" position={Position.Left} style={hidden} />
      <span className="sm-node__bar" />
      <span className="sm-node__name">{data.name}</span>
      <span className="sm-node__mark">
        {data.state === "mastered" ? <Check size={13} /> : data.key ? <Star size={13} /> : data.start ? <i className="sm-node__start">Start</i> : null}
      </span>
    </div>
  );
}

function UnitLabel({ data }: { data: UnitData }) {
  return (
    <div className="sm-unit" style={{ ["--u" as string]: unitColor(data.unit) }}>
      <span className="sm-unit__chip">Unit {data.unit}</span>
      {data.title && <span className="sm-unit__title">{data.title}</span>}
    </div>
  );
}

const nodeTypes = { topic: TopicNode, unit: UnitLabel };

export type MapMode = "all" | "path";

type Props = {
  nodes: Node[];
  edges: Edge[];
  keyIds: Set<string>;
  states: Record<string, NodeState> | null;
  selectedId: string | null;
  mode: MapMode;
  showUnsure: boolean;
  onSelect: (id: string | null) => void;
};

/** Accepted arrows give the ancestors (what must come first) and children (what it unlocks). */
function relatives(selectedId: string | null, edges: Edge[]) {
  const parents: Record<string, string[]> = {};
  const children: Record<string, string[]> = {};
  edges.filter((e) => e.band === "accepted").forEach((e) => {
    (parents[e.target] ??= []).push(e.source);
    (children[e.source] ??= []).push(e.target);
  });
  const up = new Set<string>();
  if (selectedId) {
    const stack = [selectedId];
    while (stack.length) {
      for (const p of parents[stack.pop()!] ?? []) {
        if (!up.has(p)) {
          up.add(p);
          stack.push(p);
        }
      }
    }
  }
  const next = new Set<string>(selectedId ? children[selectedId] ?? [] : []);
  return { up, next };
}

function layoutAll(nodes: Node[]) {
  const units = [...new Set(nodes.map((n) => n.unit))].sort((a, b) => a - b);
  const pos: Record<string, { x: number; y: number }> = {};
  const headers: FlowNode<UnitData>[] = [];
  let x = 0;
  for (const u of units) {
    const list = nodes.filter((n) => n.unit === u);
    const cols = Math.ceil(list.length / ROWS_PER_COLUMN);
    list.forEach((n, i) => {
      pos[n.id] = { x: x + Math.floor(i / ROWS_PER_COLUMN) * (W + COL_GAP), y: HEADER_H + (i % ROWS_PER_COLUMN) * (H + ROW_GAP) };
    });
    headers.push({
      id: `unit-${u}`,
      type: "unit",
      width: W,
      height: 44,
      position: { x, y: 0 },
      data: { unit: u, title: list[0]?.unit_title },
      selectable: false,
      draggable: false,
      focusable: false,
    });
    x += cols * (W + COL_GAP) - COL_GAP + UNIT_GAP;
  }
  return { pos, headers, colOf: (n: Node) => units.indexOf(n.unit) };
}

function layoutPath(ids: string[], edges: Edge[]) {
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: "LR", ranksep: 80, nodesep: 22, marginx: 10, marginy: 10 });
  g.setDefaultEdgeLabel(() => ({}));
  ids.forEach((id) => g.setNode(id, { width: W, height: H }));
  const set = new Set(ids);
  edges.filter((e) => set.has(e.source) && set.has(e.target) && !e.redundant && e.band === "accepted").forEach((e) => g.setEdge(e.source, e.target));
  dagre.layout(g);
  const pos: Record<string, { x: number; y: number }> = {};
  ids.forEach((id) => {
    const n = g.node(id);
    pos[id] = { x: n.x - W / 2, y: n.y - H / 2 };
  });
  return pos;
}

function Inner({ nodes, edges, keyIds, states, selectedId, mode, showUnsure, onSelect }: Props) {
  const flow = useReactFlow();
  const { up, next } = useMemo(() => relatives(selectedId, edges), [selectedId, edges]);
  const pathMode = mode === "path" && !!selectedId;

  const { flowNodes, flowEdges, related } = useMemo(() => {
    const byId = Object.fromEntries(nodes.map((n) => [n.id, n]));
    const shown = nodes.filter((n) => !pathMode || n.id === selectedId || up.has(n.id) || next.has(n.id));
    const ids = shown.map((n) => n.id);

    let pos: Record<string, { x: number; y: number }>;
    let headers: FlowNode<UnitData>[] = [];
    let colOf: (n: Node) => number = () => 0;
    if (pathMode) pos = layoutPath(ids, edges);
    else {
      const l = layoutAll(nodes);
      pos = l.pos;
      headers = l.headers;
      colOf = l.colOf;
    }

    const topic: FlowNode<TopicData>[] = shown.map((n) => {
      const look: Look = !selectedId ? "none" : n.id === selectedId ? "selected" : up.has(n.id) ? "prereq" : next.has(n.id) ? "next" : "dim";
      return {
        id: n.id,
        type: "topic",
        // fixed size: the node counts as measured at once, so nothing flickers when the layout changes
        width: W,
        height: H,
        position: pos[n.id],
        data: { name: n.name, unit: n.unit, start: n.is_start, key: keyIds.has(n.id), state: states?.[n.id]?.state, look },
      };
    });

    const inSet = new Set(ids);
    const fe: FlowEdge[] = edges
      .filter((e) => inSet.has(e.source) && inSet.has(e.target) && !e.redundant && (showUnsure || e.band === "accepted"))
      .map((e) => {
        const a = byId[e.source];
        const b = byId[e.target];
        const hot = !!selectedId && (e.target === selectedId || e.source === selectedId || (up.has(e.source) && (up.has(e.target) || e.target === selectedId)));
        const dim = !!selectedId && !hot;
        const dashed = e.band === "uncertain";
        let sourceHandle = "r";
        let targetHandle = "l";
        let type: "default" | "smoothstep" = pathMode ? "smoothstep" : "default";
        if (!pathMode) {
          const ca = colOf(a);
          const cb = colOf(b);
          if (ca === cb) {
            targetHandle = "rt";
            type = "smoothstep";
          } else if (cb < ca) {
            sourceHandle = "lt";
            targetHandle = "rt";
          }
        }
        const color = hot ? "#ff008c" : "#7c6fd0";
        return {
          id: `${e.source}->${e.target}`,
          source: e.source,
          target: e.target,
          sourceHandle,
          targetHandle,
          type,
          animated: hot && !dashed,
          zIndex: hot ? 5 : 0,
          style: {
            stroke: color,
            strokeWidth: hot ? 3.2 : 1.8 + e.confidence * 2.4,
            strokeDasharray: dashed ? "5 5" : undefined,
            opacity: dim ? 0.07 : hot ? 1 : dashed ? 0.5 : 0.75,
          },
          markerEnd: { type: MarkerType.ArrowClosed, color, width: 14, height: 14 },
        } as FlowEdge;
      });

    return { flowNodes: [...headers, ...topic] as FlowNode[], flowEdges: fe, related: [selectedId, ...up, ...next].filter(Boolean) as string[] };
  }, [nodes, edges, keyIds, states, selectedId, up, next, pathMode, showUnsure]);

  // glide the camera to whatever the user picked
  const wrap = useRef<HTMLDivElement | null>(null);
  const first = useRef(true);
  useEffect(() => {
    if (first.current) {
      first.current = false;
      return;
    }
    const t = window.setTimeout(() => {
      // the topic panel floats over the right side (or the bottom on a phone): keep the nodes clear of it
      const narrow = (wrap.current?.clientWidth ?? 1000) < 700;
      const pad: FitViewOptions["padding"] = selectedId
        ? narrow ? { top: "40px", left: "30px", right: "30px", bottom: "58%" } : { top: "70px", left: "70px", bottom: "80px", right: "380px" }
        : { top: "50px", left: "50px", right: "50px", bottom: "60px" };
      if (pathMode) flow.fitView({ padding: pad, duration: 650, maxZoom: 1.1 });
      else if (selectedId) flow.fitView({ nodes: related.map((id) => ({ id })), padding: pad, duration: 650, maxZoom: 1 });
      else flow.fitView({ padding: pad, duration: 650 });
    }, 60);
    return () => window.clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedId, pathMode]);

  return (
    <div className="sm__fill" ref={wrap}>
    <ReactFlow
      nodes={flowNodes}
      edges={flowEdges}
      nodeTypes={nodeTypes}
      nodesConnectable={false}
      nodesDraggable={false}
      elementsSelectable
      onNodeClick={(_, node) => node.type === "topic" && onSelect(node.id === selectedId ? null : node.id)}
      onPaneClick={() => onSelect(null)}
      fitView
      fitViewOptions={{ padding: 0.08 }}
      minZoom={0.12}
      maxZoom={1.6}
      proOptions={{ hideAttribution: true }}
    >
      <Background color="#d9d2f0" gap={26} size={1.6} />
      <Controls showInteractive={false} position="bottom-left" />
      {!pathMode && (
        <MiniMap
          pannable
          zoomable
          position="bottom-right"
          nodeColor={(n) => (n.type === "unit" ? "transparent" : unitColor((n.data as TopicData).unit))}
          nodeStrokeWidth={0}
          maskColor="rgba(59,48,143,0.08)"
        />
      )}
    </ReactFlow>
    </div>
  );
}

export default function StudyMap(props: Props) {
  return (
    <div className={`sm ${props.mode === "path" && props.selectedId ? "sm--path" : ""}`} data-lenis-prevent>
      <ReactFlowProvider>
        <Inner {...props} />
      </ReactFlowProvider>
    </div>
  );
}
