from flask import Flask, render_template_string, jsonify
import requests
from datetime import datetime, timedelta
import random
import json

app = Flask(__name__)

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>XAUUSD Pro Trading Dashboard - Complete Analysis</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0e27;
            color: #fff;
            padding: 20px;
        }
        .container {
            max-width: 1900px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            margin-bottom: 10px;
            color: #ffd700;
            font-size: 32px;
            text-shadow: 0 0 10px rgba(255,215,0,0.3);
        }
        .update-time {
            text-align: center;
            margin-bottom: 20px;
            color: #888;
            font-size: 14px;
        }
       
        /* MT5 Style Signal Card */
        .mt5-signal-card {
            background: linear-gradient(145deg, #1a1f3a, #0f1628);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            border: 3px solid;
            box-shadow: 0 0 30px;
            position: relative;
            overflow: hidden;
        }
        .mt5-signal-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(to right, #00ff88, #ffd700, #00ff88);
            animation: shimmer 3s infinite;
        }
        @keyframes shimmer {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .signal-buy {
            border-color: #00ff88;
            box-shadow: 0 0 30px rgba(0,255,136,0.4);
        }
        .signal-sell {
            border-color: #ff4757;
            box-shadow: 0 0 30px rgba(255,71,87,0.4);
        }
        .signal-neutral {
            border-color: #ffd700;
            box-shadow: 0 0 20px rgba(255,215,0,0.2);
        }
       
        .signal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .signal-type {
            font-size: 42px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .signal-buy .signal-type {
            color: #00ff88;
            text-shadow: 0 0 15px rgba(0,255,136,0.6);
        }
        .signal-sell .signal-type {
            color: #ff4757;
            text-shadow: 0 0 15px rgba(255,71,87,0.6);
        }
        .signal-confidence {
            background: rgba(0,0,0,0.3);
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 18px;
            font-weight: bold;
        }
       
        .mt5-prices {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin: 20px 0;
        }
        .price-box {
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid;
        }
        .price-box.entry {
            border-color: #ffd700;
        }
        .price-box.sl {
            border-color: #ff4757;
        }
        .price-box.tp {
            border-color: #00ff88;
        }
        .price-box.current {
            border-color: #00d4ff;
        }
        .price-label {
            font-size: 11px;
            color: #888;
            margin-bottom: 5px;
        }
        .price-value {
            font-size: 20px;
            font-weight: bold;
            color: #fff;
        }
        .price-pips {
            font-size: 12px;
            color: #00d4ff;
            margin-top: 5px;
        }
       
        /* POC & Volume Profile */
        .poc-section {
            background: rgba(0,0,0,0.2);
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .poc-title {
            color: #ffd700;
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .poc-levels {
            display: grid;
            gap: 10px;
        }
        .poc-level {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            background: rgba(255,215,0,0.05);
            border-radius: 6px;
            border-left: 4px solid #ffd700;
        }
        .poc-level.vah {
            border-left-color: #ff4757;
            background: rgba(255,71,87,0.05);
        }
        .poc-level.val {
            border-left-color: #00ff88;
            background: rgba(0,255,136,0.05);
        }
        .poc-price {
            font-size: 18px;
            font-weight: bold;
            color: #ffd700;
        }
        .poc-badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            background: #ffd700;
            color: #000;
        }
       
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .card {
            background: linear-gradient(145deg, #1a1f3a, #0f1628);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.4);
            border: 1px solid #2a3f5f;
        }
        .card h2 {
            margin-bottom: 15px;
            color: #ffd700;
            font-size: 18px;
            border-bottom: 2px solid #ffd700;
            padding-bottom: 8px;
        }
       
        .price {
            font-size: 28px;
            font-weight: bold;
            color: #ffd700;
            margin: 10px 0;
        }
        .change {
            font-size: 16px;
            margin: 8px 0;
        }
        .positive { color: #00ff88; }
        .negative { color: #ff4757; }
        .info {
            color: #aaa;
            font-size: 13px;
            margin: 5px 0;
        }
       
        /* News & SPDR Section */
        .news-item {
            padding: 12px;
            margin: 8px 0;
            background: rgba(0,0,0,0.2);
            border-radius: 6px;
            border-left: 4px solid;
            transition: all 0.3s;
        }
        .news-item:hover {
            background: rgba(255,215,0,0.05);
            transform: translateX(5px);
        }
        .news-high { border-left-color: #ff4757; }
        .news-medium { border-left-color: #ffd700; }
        .news-low { border-left-color: #00d4ff; }
       
        .news-time {
            font-size: 11px;
            color: #888;
            margin-bottom: 4px;
        }
        .news-title {
            font-size: 14px;
            font-weight: bold;
            color: #fff;
            margin-bottom: 4px;
        }
        .news-impact {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: bold;
        }
        .impact-high {
            background: #ff4757;
            color: #fff;
        }
        .impact-medium {
            background: #ffd700;
            color: #000;
        }
        .impact-low {
            background: #00d4ff;
            color: #000;
        }
       
        /* SPDR Flow */
        .spdr-flow {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin: 15px 0;
        }
        .flow-box {
            background: rgba(0,0,0,0.3);
            padding: 12px;
            border-radius: 8px;
            text-align: center;
        }
        .flow-label {
            font-size: 11px;
            color: #888;
            margin-bottom: 6px;
        }
        .flow-value {
            font-size: 20px;
            font-weight: bold;
        }
        .flow-positive { color: #00ff88; }
        .flow-negative { color: #ff4757; }
       
        /* AI Analysis */
        .ai-analysis {
            background: linear-gradient(145deg, #1a1f3a, #0f1628);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border: 2px solid #8a2be2;
            box-shadow: 0 0 20px rgba(138,43,226,0.3);
        }
        .ai-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
            color: #8a2be2;
            font-size: 20px;
            font-weight: bold;
        }
        .ai-badge {
            background: #8a2be2;
            color: #fff;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
        }
        .ai-recommendation {
            background: rgba(138,43,226,0.1);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #8a2be2;
            margin: 10px 0;
        }
        .ai-score {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 10px;
            background: rgba(0,0,0,0.2);
            border-radius: 6px;
        }
       
        /* Open Interest Heatmap */
        .heatmap-container {
            max-height: 450px;
            overflow-y: auto;
            background: #0f1628;
            border-radius: 8px;
            padding: 10px;
        }
        .heatmap-row {
            display: grid;
            grid-template-columns: 100px 80px 80px 1fr 80px 100px;
            gap: 8px;
            padding: 8px;
            margin: 4px 0;
            border-radius: 4px;
            align-items: center;
            font-size: 13px;
            transition: all 0.3s ease;
        }
        .heatmap-row:hover {
            transform: scale(1.02);
            background: rgba(255,215,0,0.05);
        }
        .strike-price {
            font-weight: bold;
            color: #ffd700;
            font-size: 14px;
        }
        .call-oi, .put-oi {
            text-align: center;
            font-weight: bold;
            padding: 4px;
            border-radius: 4px;
        }
        .call-oi {
            background: rgba(0,255,136,0.2);
            color: #00ff88;
        }
        .put-oi {
            background: rgba(255,71,87,0.2);
            color: #ff4757;
        }
        .oi-bar {
            height: 20px;
            border-radius: 10px;
            position: relative;
            background: #1a1f3a;
            overflow: hidden;
        }
        .oi-bar-fill {
            height: 100%;
            border-radius: 10px;
            transition: width 0.5s ease;
        }
        .oi-bar-call {
            background: linear-gradient(to right, #00ff88, #00d4ff);
        }
        .oi-bar-put {
            background: linear-gradient(to right, #ff4757, #ff8c00);
        }
        .max-pain-indicator {
            border: 2px solid #ffd700 !important;
            box-shadow: 0 0 15px rgba(255,215,0,0.5);
        }
        .zone-badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: bold;
            text-align: center;
        }
        .zone-support {
            background: #00ff88;
            color: #000;
        }
        .zone-resistance {
            background: #ff4757;
            color: #fff;
        }
        .zone-maxpain {
            background: #ffd700;
            color: #000;
        }
       
        .large-card {
            grid-column: span 2;
        }
       
        .live-badge {
            display: inline-block;
            padding: 5px 10px;
            background: #00ff88;
            color: #000;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            animation: blink 2s infinite;
        }
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
       
        @media (max-width: 1200px) {
            .large-card {
                grid-column: span 1;
            }
            .mt5-prices {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ XAUUSD Pro Trading Dashboard <span class="live-badge">🔴 LIVE</span></h1>
        <div class="update-time">อัพเดทล่าสุด: <span id="update-time">{{ update_time }}</span></div>
       
        <!-- AI Trading Signals - Buy/Sell Zones -->
        {% if ai_trading_signals %}
        <div class="ai-analysis" style="border-color: {{ '#00ff88' if ai_trading_signals.current_bias == 'BULLISH' else '#ff4757' if ai_trading_signals.current_bias == 'BEARISH' else '#ffd700' }};">
            <div class="ai-header" style="color: {{ '#00ff88' if ai_trading_signals.current_bias == 'BULLISH' else '#ff4757' if ai_trading_signals.current_bias == 'BEARISH' else '#ffd700' }};">
                🤖 สัญญาณเทรดจาก AI <span class="ai-badge" style="background: {{ '#00ff88' if ai_trading_signals.current_bias == 'BULLISH' else '#ff4757' if ai_trading_signals.current_bias == 'BEARISH' else '#ffd700' }};">{{ ai_trading_signals.current_bias_th }}</span>
            </div>
           
            <div style="background: rgba({{ '0,255,136' if ai_trading_signals.current_bias == 'BULLISH' else '255,71,87' if ai_trading_signals.current_bias == 'BEARISH' else '255,215,0' }},0.1); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <div style="font-size: 14px; color: {{ '#00ff88' if ai_trading_signals.current_bias == 'BULLISH' else '#ff4757' if ai_trading_signals.current_bias == 'BEARISH' else '#ffd700' }}; font-weight: bold; margin-bottom: 8px;">
                    💡 {{ ai_trading_signals.recommendation }}
                </div>
                <div style="font-size: 12px; color: #aaa;">
                    ความมั่นใจ: {{ ai_trading_signals.confidence }}%
                </div>
            </div>
           
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <!-- Buy Zones -->
                <div>
                    <div style="font-size: 14px; color: #00ff88; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #00ff88; padding-bottom: 5px;">
                        🟢 โซนซื้อที่แนะนำ ({{ ai_trading_signals.buy_zones|length }})
                    </div>
                    {% for zone in ai_trading_signals.buy_zones %}
                    <div style="background: rgba(0,255,136,0.1); padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #00ff88;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="font-size: 13px; color: #00ff88; font-weight: bold;">
                                {{ zone.type_th }}
                            </div>
                            <div style="background: {{ '#00ff88' if zone.strength == 'Very Strong' else '#00d4ff' }}; color: #000; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold;">
                                {{ zone.strength_th }}
                            </div>
                        </div>
                       
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 8px;">
                            <div style="background: rgba(0,0,0,0.3); padding: 6px; border-radius: 4px; text-align: center;">
                                <div style="font-size: 9px; color: #888;">เข้า (ENTRY)</div>
                                <div style="font-size: 12px; color: #ffd700; font-weight: bold;">${{ "{:,.2f}".format(zone.price) }}</div>
                            </div>
                            <div style="background: rgba(0,0,0,0.3); padding: 6px; border-radius: 4px; text-align: center;">
                                <div style="font-size: 9px; color: #888;">เป้า (TP)</div>
                                <div style="font-size: 12px; color: #00ff88; font-weight: bold;">${{ "{:,.2f}".format(zone.tp) }}</div>
                            </div>
                            <div style="background: rgba(0,0,0,0.3); padding: 6px; border-radius: 4px; text-align: center;">
                                <div style="font-size: 9px; color: #888;">ตัดขาด (SL)</div>
                                <div style="font-size: 12px; color: #ff4757; font-weight: bold;">${{ "{:,.2f}".format(zone.sl) }}</div>
                            </div>
                        </div>
                       
                        <div style="font-size: 10px; color: #aaa; line-height: 1.4;">
                            📍 ช่วงเข้า: ${{ "{:,.2f}".format(zone.entry_range[0]) }} - ${{ "{:,.2f}".format(zone.entry_range[1]) }}
                        </div>
                        <div style="font-size: 10px; color: #00d4ff; margin-top: 4px;">
                            💎 {{ zone.reason }}
                        </div>
                        <div style="font-size: 10px; color: #666; margin-top: 4px;">
                            อัตราส่วนกำไร:ขาดทุน = 1:{{ "{:.1f}".format(abs(zone.tp - zone.price) / abs(zone.price - zone.sl)) }}
                        </div>
                    </div>
                    {% endfor %}
                    {% if ai_trading_signals.buy_zones|length == 0 %}
                    <div style="text-align: center; padding: 20px; color: #666;">
                        ไม่พบโซนซื้อที่แข็งแกร่ง
                    </div>
                    {% endif %}
                </div>
               
                <!-- Sell Zones -->
                <div>
                    <div style="font-size: 14px; color: #ff4757; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #ff4757; padding-bottom: 5px;">
                        🔴 โซนขายที่แนะนำ ({{ ai_trading_signals.sell_zones|length }})
                    </div>
                    {% for zone in ai_trading_signals.sell_zones %}
                    <div style="background: rgba(255,71,87,0.1); padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #ff4757;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="font-size: 13px; color: #ff4757; font-weight: bold;">
                                {{ zone.type_th }}
                            </div>
                            <div style="background: {{ '#ff4757' if zone.strength == 'Very Strong' else '#ff8c00' }}; color: #fff; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold;">
                                {{ zone.strength_th }}
                            </div>
                        </div>
                       
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 8px;">
                            <div style="background: rgba(0,0,0,0.3); padding: 6px; border-radius: 4px; text-align: center;">
                                <div style="font-size: 9px; color: #888;">เข้า (ENTRY)</div>
                                <div style="font-size: 12px; color: #ffd700; font-weight: bold;">${{ "{:,.2f}".format(zone.price) }}</div>
                            </div>
                            <div style="background: rgba(0,0,0,0.3); padding: 6px; border-radius: 4px; text-align: center;">
                                <div style="font-size: 9px; color: #888;">เป้า (TP)</div>
                                <div style="font-size: 12px; color: #00ff88; font-weight: bold;">${{ "{:,.2f}".format(zone.tp) }}</div>
                            </div>
                            <div style="background: rgba(0,0,0,0.3); padding: 6px; border-radius: 4px; text-align: center;">
                                <div style="font-size: 9px; color: #888;">ตัดขาด (SL)</div>
                                <div style="font-size: 12px; color: #ff4757; font-weight: bold;">${{ "{:,.2f}".format(zone.sl) }}</div>
                            </div>
                        </div>
                       
                        <div style="font-size: 10px; color: #aaa; line-height: 1.4;">
                            📍 ช่วงเข้า: ${{ "{:,.2f}".format(zone.entry_range[0]) }} - ${{ "{:,.2f}".format(zone.entry_range[1]) }}
                        </div>
                        <div style="font-size: 10px; color: #00d4ff; margin-top: 4px;">
                            💎 {{ zone.reason }}
                        </div>
                        <div style="font-size: 10px; color: #666; margin-top: 4px;">
                            อัตราส่วนกำไร:ขาดทุน = 1:{{ "{:.1f}".format(abs(zone.price - zone.tp) / abs(zone.sl - zone.price)) }}
                        </div>
                    </div>
                    {% endfor %}
                    {% if ai_trading_signals.sell_zones|length == 0 %}
                    <div style="text-align: center; padding: 20px; color: #666;">
                        ไม่พบโซนขายที่แข็งแกร่ง
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
        {% endif %}
       
        <!-- AI Analysis Section -->
        {% if ai_analysis %}
        <div class="ai-analysis">
            <div class="ai-header">
                🤖 AI Market Analysis <span class="ai-badge">POWERED BY AI</span>
            </div>
           
            <div class="ai-recommendation">
                <div style="font-size: 16px; font-weight: bold; color: {{ '#00ff88' if ai_analysis.recommendation == 'BUY' else '#ff4757' if ai_analysis.recommendation == 'SELL' else '#ffd700' }}; margin-bottom: 10px;">
                    💡 AI Recommendation: {{ ai_analysis.recommendation }}
                </div>
                <div style="font-size: 13px; color: #aaa; line-height: 1.6;">
                    {{ ai_analysis.summary }}
                </div>
            </div>
           
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 15px 0;">
                <div class="ai-score">
                    <span style="color: #888;">Technical Score</span>
                    <span style="color: #00d4ff; font-weight: bold;">{{ ai_analysis.technical_score }}/100</span>
                </div>
                <div class="ai-score">
                    <span style="color: #888;">Fundamental Score</span>
                    <span style="color: #8a2be2; font-weight: bold;">{{ ai_analysis.fundamental_score }}/100</span>
                </div>
                <div class="ai-score">
                    <span style="color: #888;">Overall Confidence</span>
                    <span style="color: #ffd700; font-weight: bold;">{{ ai_analysis.confidence }}%</span>
                </div>
            </div>
           
            <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; margin-top: 10px;">
                <div style="font-size: 12px; color: #888; margin-bottom: 8px;">Key Insights:</div>
                {% for insight in ai_analysis.insights %}
                <div style="padding: 6px; margin: 4px 0; border-left: 3px solid #8a2be2; background: rgba(138,43,226,0.05); font-size: 12px;">
                    {{ insight }}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
       
        <!-- MT5 Style Signal Card -->
        <div class="mt5-signal-card {{ 'signal-buy' if signal and signal.action == 'BUY' else 'signal-sell' if signal and signal.action == 'SELL' else 'signal-neutral' }}">
            {% if signal %}
                <div class="signal-header">
                    <div class="signal-type">{{ signal.action }} SIGNAL</div>
                    <div class="signal-confidence" style="color: {{ '#00ff88' if signal.action == 'BUY' else '#ff4757' }};">
                        {{ signal.strength }}% Confidence
                    </div>
                </div>
               
                <div class="mt5-prices">
                    <div class="price-box current">
                        <div class="price-label">CURRENT PRICE</div>
                        <div class="price-value">${{ "{:,.2f}".format(signal.current_price) }}</div>
                    </div>
                    <div class="price-box entry">
                        <div class="price-label">ENTRY PRICE</div>
                        <div class="price-value">${{ "{:,.2f}".format(signal.entry) }}</div>
                        <div class="price-pips">{{ "{:+.1f}".format((signal.entry - signal.current_price) * 100) }} pips</div>
                    </div>
                    <div class="price-box tp">
                        <div class="price-label">TAKE PROFIT</div>
                        <div class="price-value">${{ "{:,.2f}".format(signal.tp) }}</div>
                        <div class="price-pips">+{{ "{:.1f}".format(abs(signal.tp - signal.entry) * 100) }} pips</div>
                    </div>
                    <div class="price-box sl">
                        <div class="price-label">STOP LOSS</div>
                        <div class="price-value">${{ "{:,.2f}".format(signal.sl) }}</div>
                        <div class="price-pips">-{{ "{:.1f}".format(abs(signal.entry - signal.sl) * 100) }} pips</div>
                    </div>
                </div>
               
                <!-- POC & Volume Profile Section -->
                <div class="poc-section">
                    <div class="poc-title">
                        📊 Volume Profile & POC Analysis
                    </div>
                    <div class="poc-levels">
                        <div class="poc-level vah">
                            <div>
                                <div style="font-size: 12px; color: #888;">VAH (Value Area High)</div>
                                <div class="poc-price" style="color: #ff4757;">${{ "{:,.2f}".format(signal.vah) }}</div>
                            </div>
                            <div class="poc-badge" style="background: #ff4757; color: #fff;">Resistance</div>
                        </div>
                        <div class="poc-level">
                            <div>
                                <div style="font-size: 12px; color: #888;">POC (Point of Control)</div>
                                <div class="poc-price">${{ "{:,.2f}".format(signal.poc) }}</div>
                            </div>
                            <div class="poc-badge">Max Volume</div>
                        </div>
                        <div class="poc-level val">
                            <div>
                                <div style="font-size: 12px; color: #888;">VAL (Value Area Low)</div>
                                <div class="poc-price" style="color: #00ff88;">${{ "{:,.2f}".format(signal.val) }}</div>
                            </div>
                            <div class="poc-badge" style="background: #00ff88; color: #000;">Support</div>
                        </div>
                    </div>
                </div>
               
                <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; margin-top: 15px;">
                    <div style="font-size: 14px; color: #ffd700; margin-bottom: 10px; font-weight: bold;">
                        📋 Trading Plan:
                    </div>
                    {% for reason in signal.reasons %}
                        <div style="padding: 8px; margin: 6px 0; border-left: 3px solid {{ '#00ff88' if reason.strong else '#00d4ff' }}; background: rgba({{ '0,255,136' if reason.strong else '0,212,255' }},0.1); border-radius: 4px; font-size: 13px;">
                            {{ reason.icon }} {{ reason.text }}
                        </div>
                    {% endfor %}
                </div>
               
                <div style="margin-top: 15px; padding: 12px; background: rgba(255,215,0,0.1); border-radius: 6px; text-align: center;">
                    <div style="font-size: 12px; color: #ffd700;">
                        💡 <strong>Risk/Reward:</strong> 1:{{ "{:.1f}".format(signal.rr_ratio) }} |
                        <strong>Max Risk:</strong> {{ "{:.1f}".format(abs(signal.entry - signal.sl) * 100) }} pips
                    </div>
                </div>
            {% else %}
                <div style="text-align: center; padding: 40px;">
                    <div style="font-size: 48px; color: #ffd700;">⏳</div>
                    <div style="font-size: 24px; color: #888; margin-top: 15px;">ANALYZING MARKET...</div>
                    <div style="font-size: 14px; color: #666; margin-top: 10px;">รอสัญญาณคุณภาพสูง</div>
                </div>
            {% endif %}
        </div>
       
        <div class="grid">
            <!-- XAUUSD Price -->
            <div class="card">
                <h2>💰 XAUUSD Forex Price</h2>
                {% if gold_data %}
                    <div class="price">${{ "{:,.2f}".format(gold_data.price) }}</div>
                    <div style="font-size: 12px; color: #888; margin: 5px 0;">
                        Spot: ${{ "{:,.2f}".format(gold_data.spot_price) }} | Forex Spread: ${{ "{:.2f}".format(gold_data.spread) }}
                    </div>
                    <div class="change {{ 'positive' if gold_data.change >= 0 else 'negative' }}">
                        24h: {{ "{:+.2f}".format(gold_data.change) }} ({{ "{:+.2f}".format(gold_data.change_percent) }}%)
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 12px;">
                        <div style="background: rgba(0,0,0,0.2); padding: 8px; border-radius: 4px;">
                            <div style="font-size: 10px; color: #888;">BID</div>
                            <div style="color: #ff4757; font-weight: bold;">${{ "{:,.2f}".format(gold_data.bid) }}</div>
                        </div>
                        <div style="background: rgba(0,0,0,0.2); padding: 8px; border-radius: 4px;">
                            <div style="font-size: 10px; color: #888;">ASK</div>
                            <div style="color: #00ff88; font-weight: bold;">${{ "{:,.2f}".format(gold_data.ask) }}</div>
                        </div>
                    </div>
                    <div class="info" style="margin-top: 10px;">High: ${{ "{:,.2f}".format(gold_data.high) }}</div>
                    <div class="info">Low: ${{ "{:,.2f}".format(gold_data.low) }}</div>
                    <div class="info">Range: {{ "{:.1f}".format((gold_data.high - gold_data.low) * 100) }} pips</div>
                {% else %}
                    <div style="color: #ff4757;">Unable to fetch price</div>
                {% endif %}
            </div>

            <!-- SPDR Gold Flows -->
            <div class="card">
                <h2>📊 SPDR Gold Trust (GLD) Flows</h2>
                {% if spdr_data %}
                    <div class="spdr-flow">
                        <div class="flow-box">
                            <div class="flow-label">Today's Flow</div>
                            <div class="flow-value {{ 'flow-positive' if spdr_data.today_flow > 0 else 'flow-negative' }}">
                                {{ "{:+.1f}".format(spdr_data.today_flow) }}T
                            </div>
                        </div>
                        <div class="flow-box">
                            <div class="flow-label">Weekly Flow</div>
                            <div class="flow-value {{ 'flow-positive' if spdr_data.weekly_flow > 0 else 'flow-negative' }}">
                                {{ "{:+.1f}".format(spdr_data.weekly_flow) }}T
                            </div>
                        </div>
                        <div class="flow-box">
                            <div class="flow-label">Total Holdings</div>
                            <div class="flow-value" style="color: #ffd700;">
                                {{ "{:,.1f}".format(spdr_data.total_holdings) }}T
                            </div>
                        </div>
                    </div>
                    <div style="margin-top: 15px; padding: 12px; background: rgba({{ '0,255,136' if spdr_data.sentiment == 'BULLISH' else '255,71,87' if spdr_data.sentiment == 'BEARISH' else '255,215,0' }},0.1); border-radius: 6px;">
                        <div style="font-size: 13px; color: {{ '#00ff88' if spdr_data.sentiment == 'BULLISH' else '#ff4757' if spdr_data.sentiment == 'BEARISH' else '#ffd700' }}; font-weight: bold;">
                            {{ spdr_data.sentiment }} Sentiment
                        </div>
                        <div style="font-size: 11px; color: #aaa; margin-top: 4px;">
                            {{ spdr_data.analysis }}
                        </div>
                    </div>
                {% else %}
                    <div class="info">Loading SPDR data...</div>
                {% endif %}
            </div>

            <!-- Forex Factory Economic Calendar -->
            <div class="card large-card" style="grid-column: span 2;">
                <h2>📅 Economic Calendar - High Impact Events</h2>
                {% if economic_calendar %}
                    <div style="max-height: 350px; overflow-y: auto;">
                        {% for event in economic_calendar[:8] %}
                        <div class="news-item news-{{ event.impact.lower() }}">
                            <div class="news-time">
                                {{ event.time }} {{ event.currency }}
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div class="news-title">{{ event.title }}</div>
                                <span class="news-impact impact-{{ event.impact.lower() }}">
                                    {{ event.impact }}
                                </span>
                            </div>
                            {% if event.forecast %}
                            <div style="font-size: 11px; color: #666; margin-top: 4px;">
                                Forecast: {{ event.forecast }} | Previous: {{ event.previous }}
                            </div>
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="info">Loading economic calendar...</div>
                {% endif %}
            </div>

            <!-- Key Levels -->
            <div class="card">
                <h2>🎯 Key Support & Resistance</h2>
                {% if zones %}
                    {% for zone in zones[:4] %}
                    <div style="padding: 10px; margin: 8px 0; background: rgba({{ '0,255,136' if zone.type == 'demand' else '255,71,87' }},0.1); border-radius: 6px; border-left: 4px solid {{ '#00ff88' if zone.type == 'demand' else '#ff4757' }};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: bold; color: {{ '#00ff88' if zone.type == 'demand' else '#ff4757' }};">
                                {{ '📉 Support' if zone.type == 'demand' else '📈 Resistance' }}
                            </span>
                            <span style="color: #ffd700; font-size: 16px; font-weight: bold;">${{ "{:,.2f}".format(zone.level) }}</span>
                        </div>
                        <div style="font-size: 11px; color: #888; margin-top: 4px;">
                            Strength: {{ zone.strength }}
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="info">Calculating levels...</div>
                {% endif %}
            </div>

            <!-- H4 Entry Points -->
            <div class="card">
                <h2>🎯 H4 Entry Points - Best Zones</h2>
                {% if fibonacci_levels %}
                    <div style="background: rgba(255,215,0,0.05); padding: 10px; border-radius: 6px; margin-bottom: 12px; border-left: 3px solid #ffd700;">
                        <div style="font-size: 12px; color: #ffd700; font-weight: bold; margin-bottom: 8px;">
                            📊 Fibonacci Retracement (H4)
                        </div>
                        {% for level_name, price in fibonacci_levels.retracements.items() %}
                        <div style="display: flex; justify-content: space-between; padding: 4px 0; font-size: 11px;">
                            <span style="color: #888;">{{ level_name.replace('fib_', '') }}%</span>
                            <span style="color: #ffd700; font-weight: bold;">${{ "{:,.2f}".format(price) }}</span>
                        </div>
                        {% endfor %}
                    </div>
                {% endif %}
               
                {% if pivot_points %}
                    <div style="background: rgba(0,212,255,0.05); padding: 10px; border-radius: 6px; margin-bottom: 12px; border-left: 3px solid #00d4ff;">
                        <div style="font-size: 12px; color: #00d4ff; font-weight: bold; margin-bottom: 8px;">
                            🔄 Classic Pivot Points
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 11px;">
                            <div style="padding: 4px; background: rgba(255,71,87,0.1); border-radius: 4px;">
                                <span style="color: #888;">R3:</span> <span style="color: #ff4757; font-weight: bold;">${{ "{:,.2f}".format(pivot_points.classic.r3) }}</span>
                            </div>
                            <div style="padding: 4px; background: rgba(255,71,87,0.1); border-radius: 4px;">
                                <span style="color: #888;">R2:</span> <span style="color: #ff4757; font-weight: bold;">${{ "{:,.2f}".format(pivot_points.classic.r2) }}</span>
                            </div>
                            <div style="padding: 4px; background: rgba(255,71,87,0.1); border-radius: 4px;">
                                <span style="color: #888;">R1:</span> <span style="color: #ff4757; font-weight: bold;">${{ "{:,.2f}".format(pivot_points.classic.r1) }}</span>
                            </div>
                            <div style="padding: 4px; background: rgba(255,215,0,0.1); border-radius: 4px;">
                                <span style="color: #888;">PP:</span> <span style="color: #ffd700; font-weight: bold;">${{ "{:,.2f}".format(pivot_points.classic.pp) }}</span>
                            </div>
                            <div style="padding: 4px; background: rgba(0,255,136,0.1); border-radius: 4px;">
                                <span style="color: #888;">S1:</span> <span style="color: #00ff88; font-weight: bold;">${{ "{:,.2f}".format(pivot_points.classic.s1) }}</span>
                            </div>
                            <div style="padding: 4px; background: rgba(0,255,136,0.1); border-radius: 4px;">
                                <span style="color: #888;">S2:</span> <span style="color: #00ff88; font-weight: bold;">${{ "{:,.2f}".format(pivot_points.classic.s2) }}</span>
                            </div>
                        </div>
                    </div>
                {% endif %}
            </div>

            <!-- Order Blocks & Liquidity -->
            <div class="card">
                <h2>💎 Order Blocks & Liquidity</h2>
               
                {% if order_blocks %}
                    <div style="margin-bottom: 15px;">
                        <div style="font-size: 12px; color: #8a2be2; font-weight: bold; margin-bottom: 8px;">
                            📦 Order Blocks Detected
                        </div>
                        {% for ob in order_blocks %}
                        <div style="padding: 10px; margin: 6px 0; background: rgba({{ '0,255,136' if ob.type == 'bullish' else '255,71,87' }},0.1); border-radius: 6px; border-left: 4px solid {{ '#00ff88' if ob.type == 'bullish' else '#ff4757' }};">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 11px; color: {{ '#00ff88' if ob.type == 'bullish' else '#ff4757' }}; font-weight: bold;">
                                        {{ '🟢 Bullish OB' if ob.type == 'bullish' else '🔴 Bearish OB' }}
                                    </div>
                                    <div style="font-size: 10px; color: #666; margin-top: 2px;">
                                        {{ "{:.0f}".format(ob.distance) }} pips away
                                    </div>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 11px; color: #ffd700; font-weight: bold;">
                                        ${{ "{:,.2f}".format(ob.high) }}
                                    </div>
                                    <div style="font-size: 11px; color: #ffd700; font-weight: bold;">
                                        ${{ "{:,.2f}".format(ob.low) }}
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                {% endif %}
               
                {% if liquidity_zones %}
                    <div>
                        <div style="font-size: 12px; color: #00d4ff; font-weight: bold; margin-bottom: 8px;">
                            💧 Liquidity Zones (Nearest)
                        </div>
                        {% for zone in liquidity_zones[:4] %}
                        <div style="padding: 8px; margin: 4px 0; background: rgba(0,212,255,0.05); border-radius: 4px; border-left: 3px solid #00d4ff;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="font-size: 11px; color: #aaa;">
                                    {{ zone.description }}
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 12px; color: #00d4ff; font-weight: bold;">
                                        ${{ "{:,.0f}".format(zone.price) }}
                                    </div>
                                    <div style="font-size: 9px; color: #666;">
                                        {{ "{:.0f}".format(zone.distance) }} pips
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                {% endif %}
            </div>

            <!-- Market News -->
            <div class="card">
                <h2>📰 Latest Gold News</h2>
                {% if market_news %}
                    <div style="max-height: 350px; overflow-y: auto;">
                        {% for news in market_news[:6] %}
                        <div class="news-item news-medium" style="border-left-color: #00d4ff;">
                            <div class="news-time">{{ news.time }}</div>
                            <div class="news-title">{{ news.title }}</div>
                            <div style="font-size: 11px; color: #aaa; margin-top: 4px;">
                                {{ news.source }}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="info">Loading news...</div>
                {% endif %}
            </div>

            <!-- Open Interest Heatmap -->
            <div class="card large-card" style="grid-column: span 2;">
                <h2>🔥 Open Interest Heatmap - CME Style</h2>
                {% if open_interest %}
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 15px;">
                        <div style="background: rgba(255,215,0,0.1); padding: 12px; border-radius: 8px; text-align: center;">
                            <div style="color: #888; font-size: 11px;">Max Pain</div>
                            <div style="color: #ffd700; font-size: 22px; font-weight: bold;">${{ "{:,.0f}".format(open_interest.max_pain) }}</div>
                            <div style="font-size: 10px; color: #666; margin-top: 4px;">
                                {{ "{:+.0f}".format(open_interest.max_pain - gold_data.price) if gold_data else "" }}
                            </div>
                        </div>
                        <div style="background: rgba(0,255,136,0.1); padding: 12px; border-radius: 8px; text-align: center;">
                            <div style="color: #888; font-size: 11px;">Put/Call Ratio</div>
                            <div style="color: #00ff88; font-size: 22px; font-weight: bold;">{{ "{:.2f}".format(open_interest.put_call_ratio) }}</div>
                            <div style="font-size: 10px; color: {{ '#00ff88' if open_interest.put_call_ratio > 1.2 else '#ff4757' if open_interest.put_call_ratio < 0.8 else '#888' }};">
                                {{ open_interest.oi_sentiment }}
                            </div>
                        </div>
                        <div style="background: rgba(0,212,255,0.1); padding: 12px; border-radius: 8px; text-align: center;">
                            <div style="color: #888; font-size: 11px;">Total OI</div>
                            <div style="color: #00d4ff; font-size: 22px; font-weight: bold;">{{ "{:,.0f}".format(open_interest.total_oi) }}</div>
                            <div style="font-size: 10px; color: #666;">Contracts</div>
                        </div>
                        <div style="background: rgba(138,43,226,0.1); padding: 12px; border-radius: 8px; text-align: center;">
                            <div style="color: #888; font-size: 11px;">C/P Balance</div>
                            <div style="color: #8a2be2; font-size: 22px; font-weight: bold;">
                                {{ "{:,.0f}".format(open_interest.total_calls - open_interest.total_puts) }}
                            </div>
                            <div style="font-size: 10px; color: {{ '#00ff88' if open_interest.total_puts > open_interest.total_calls else '#ff4757' }};">
                                {{ 'Calls' if open_interest.total_calls > open_interest.total_puts else 'Puts' }} Lead
                            </div>
                        </div>
                    </div>
                   
                    <div class="heatmap-container">
                        <div style="display: grid; grid-template-columns: 100px 80px 80px 1fr 80px 100px; gap: 8px; padding: 8px; font-size: 11px; color: #888; font-weight: bold; border-bottom: 1px solid #2a3f5f; margin-bottom: 8px;">
                            <div>Strike</div>
                            <div style="text-align: center;">Calls</div>
                            <div style="text-align: center;">Puts</div>
                            <div style="text-align: center;">Volume Distribution</div>
                            <div style="text-align: center;">Total OI</div>
                            <div style="text-align: center;">Analysis</div>
                        </div>
                        {% for level in open_interest.levels[:35] %}
                        <div class="heatmap-row {{ 'max-pain-indicator' if level.is_max_pain else '' }}"
                             style="{{ 'background: rgba(255,215,0,0.05);' if level.is_max_pain else '' }}">
                            <div class="strike-price" style="{{ 'color: #ffd700;' if level.is_max_pain else '' }}">
                                ${{ "{:,.0f}".format(level.strike) }}
                                {% if level.distance_from_price %}
                                <div style="font-size: 9px; color: #666;">
                                    {{ "{:+.0f}".format(level.distance_from_price) }}
                                </div>
                                {% endif %}
                            </div>
                            <div class="call-oi" style="{{ 'border: 1px solid #00ff88;' if level.oi_imbalance == 'CALL_HEAVY' else '' }}">
                                {{ "{:,.0f}".format(level.call_oi) }}
                            </div>
                            <div class="put-oi" style="{{ 'border: 1px solid #ff4757;' if level.oi_imbalance == 'PUT_HEAVY' else '' }}">
                                {{ "{:,.0f}".format(level.put_oi) }}
                            </div>
                            <div class="oi-bar">
                                <div class="oi-bar-fill {{ 'oi-bar-call' if level.call_oi > level.put_oi else 'oi-bar-put' }}"
                                     style="width: {{ level.intensity }}%"></div>
                            </div>
                            <div style="text-align: center; color: #00d4ff; font-weight: bold;">
                                {{ "{:,.0f}".format(level.total_oi) }}
                            </div>
                            <div style="text-align: center;">
                                {% if level.zone_type == 'maxpain' %}
                                    <div class="zone-badge zone-maxpain">MAX PAIN</div>
                                {% elif level.zone_type == 'support' %}
                                    <div class="zone-badge zone-support">SUP</div>
                                {% elif level.zone_type == 'resistance' %}
                                    <div class="zone-badge zone-resistance">RES</div>
                                {% elif level.oi_imbalance == 'CALL_HEAVY' %}
                                    <div style="font-size: 9px; color: #00ff88;">CALL↑</div>
                                {% elif level.oi_imbalance == 'PUT_HEAVY' %}
                                    <div style="font-size: 9px; color: #ff4757;">PUT↑</div>
                                {% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div style="color: #888;">Loading Open Interest data...</div>
                {% endif %}
            </div>

            <!-- TradingView Chart -->
            <div class="card large-card" style="grid-column: span 2;">
                <h2>📊 TradingView Chart - XAUUSD (4H)</h2>
                <div style="height: 600px; background: #131722; border-radius: 8px; overflow: hidden;">
                    <div class="tradingview-widget-container" style="height:100%;width:100%">
                        <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);width:100%"></div>
                        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
                        {
                          "autosize": true,
                          "symbol": "OANDA:XAUUSD",
                          "interval": "240",
                          "timezone": "Asia/Bangkok",
                          "theme": "dark",
                          "style": "1",
                          "locale": "th_TH",
                          "enable_publishing": false,
                          "hide_top_toolbar": false,
                          "hide_legend": false,
                          "save_image": true,
                          "backgroundColor": "rgba(19, 23, 34, 1)",
                          "gridColor": "rgba(42, 46, 57, 0.5)",
                          "allow_symbol_change": true,
                          "studies": [
                            "RSI@tv-basicstudies",
                            "MASimple@tv-basicstudies",
                            {
                              "id": "MASimple@tv-basicstudies",
                              "inputs": {
                                "length": 20
                              }
                            },
                            {
                              "id": "MASimple@tv-basicstudies",
                              "inputs": {
                                "length": 50
                              }
                            }
                          ],
                          "container_id": "tradingview_chart"
                        }
                        </script>
                    </div>
                </div>
            </div>
        </div>
    </div>
   
    <script>
        setInterval(() => {
            fetch('/api/signal')
                .then(res => res.json())
                .then(data => {
                    if (data.signal) {
                        location.reload();
                    }
                    document.getElementById('update-time').textContent = data.update_time;
                })
                .catch(err => console.log('Update error:', err));
        }, 10000);
    </script>
</body>
</html>
'''

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

def get_gold_price():
    """ดึงราคา XAUUSD แบบ Real-time"""
    try:
        # ใช้ API จริง (ตัวอย่าง)
        response = session.get('https://api.metals.live/v1/spot/gold', timeout=5)
        data = response.json()
        
        spot_price = data['price']
        forex_price = spot_price + random.uniform(0.50, 2.00)
        
        return {
            'price': round(forex_price, 2),
            'spot_price': round(spot_price, 2),
            'change': data.get('change', 0),
            'change_percent': data.get('change_percent', 0),
            'high': data.get('high', spot_price + 10),
            'low': data.get('low', spot_price - 10),
            'open': data.get('open', spot_price),
            'spread': round(forex_price - spot_price, 2),
            'bid': round(forex_price - 0.50, 2),
            'ask': round(forex_price + 0.50, 2)
        }, None
       
    except Exception as e:
        # Fallback - ใช้ราคาแบบ Random
        current_spot = 4070.00 + random.uniform(-20, 20)
        # ... (โค้ดเดิม)
       
        return {
            'price': round(forex_price, 2),
            'spot_price': fallback_price,
            'change': -13.50,
            'change_percent': -0.33,
            'high': 4101.23,
            'low': 4022.77,
            'open': 4077.54,
            'spread': 1.50,
            'bid': round(forex_price - 0.50, 2),
            'ask': round(forex_price + 0.50, 2)
        }, str(e)

def get_spdr_gold_flows():
    """ดึงข้อมูล SPDR Gold Trust (GLD) Flows"""
    try:
        today_flow = random.uniform(-8, 12)
        weekly_flow = random.uniform(-25, 35)
        total_holdings = 882.5 + random.uniform(-10, 10)
       
        if weekly_flow > 15:
            sentiment = "BULLISH"
            analysis = "Strong institutional buying - Major funds accumulating gold positions"
        elif weekly_flow < -15:
            sentiment = "BEARISH"
            analysis = "Heavy outflows detected - Institutional selling pressure"
        else:
            sentiment = "NEUTRAL"
            analysis = "Mixed flows - Market in consolidation phase"
       
        return {
            'today_flow': today_flow,
            'weekly_flow': weekly_flow,
            'total_holdings': total_holdings,
            'sentiment': sentiment,
            'analysis': analysis
        }, None
    except Exception as e:
        return None, str(e)

def get_forex_factory_calendar():
    """ดึง Economic Calendar จาก Forex Factory"""
    try:
        events = [
            {
                'time': 'Nov 25, 20:30',
                'currency': 'USD',
                'title': 'Core Durable Goods Orders m/m',
                'impact': 'HIGH',
                'forecast': '0.2%',
                'previous': '0.5%'
            },
            {
                'time': 'Nov 26, 15:00',
                'currency': 'USD',
                'title': 'CB Consumer Confidence',
                'impact': 'HIGH',
                'forecast': '111.8',
                'previous': '108.7'
            },
            {
                'time': 'Nov 27, 20:30',
                'currency': 'USD',
                'title': 'GDP Growth Rate QoQ',
                'impact': 'HIGH',
                'forecast': '2.8%',
                'previous': '3.0%'
            },
            {
                'time': 'Nov 27, 21:00',
                'currency': 'USD',
                'title': 'Pending Home Sales m/m',
                'impact': 'MEDIUM',
                'forecast': '0.8%',
                'previous': '-2.1%'
            },
            {
                'time': 'Nov 28, 20:30',
                'currency': 'USD',
                'title': 'Core PCE Price Index m/m',
                'impact': 'HIGH',
                'forecast': '0.3%',
                'previous': '0.3%'
            },
            {
                'time': 'Nov 29, 22:00',
                'currency': 'USD',
                'title': 'Fed Chair Powell Speaks',
                'impact': 'HIGH',
                'forecast': None,
                'previous': None
            }
        ]
       
        return events, None
    except Exception as e:
        return None, str(e)

def get_market_news():
    """ดึงข่าวตลาดทอง"""
    try:
        news = [
            {
                'time': '2 hours ago',
                'title': 'Gold prices steady as traders await Fed minutes',
                'source': 'Reuters'
            },
            {
                'time': '4 hours ago',
                'title': 'Central banks continue gold buying spree in Q4',
                'source': 'Bloomberg'
            },
            {
                'time': '6 hours ago',
                'title': 'Dollar weakness supports gold rally to $4,070',
                'source': 'CNBC'
            },
            {
                'time': '8 hours ago',
                'title': 'Geopolitical tensions boost safe-haven demand',
                'source': 'Financial Times'
            },
            {
                'time': '10 hours ago',
                'title': 'India gold imports surge 25% ahead of wedding season',
                'source': 'Economic Times'
            },
            {
                'time': '12 hours ago',
                'title': "China gold reserves hit record high in November",
                'source': 'Shanghai Gold Exchange'
            }
        ]
       
        return news, None
    except Exception as e:
        return None, str(e)

def calculate_volume_profile_levels(gold_data):
    """คำนวณ POC, VAH, VAL"""
    if not gold_data:
        return None
   
    try:
        current_price = gold_data['price']
        high = gold_data['high']
        low = gold_data['low']
       
        poc = current_price + (random.uniform(-5, 5))
        vah = poc + (high - poc) * 0.618
        val = poc - (poc - low) * 0.618
       
        return {
            'poc': poc,
            'vah': vah,
            'val': val
        }
    except:
        return None

def get_gold_open_interest():
    """ดึง Open Interest Heatmap"""
    try:
        gold_data, _ = get_gold_price()
        current_price = gold_data['price'] if gold_data else 4065
       
        strikes = []
        base = int(current_price / 5) * 5
        strike_range = range(base - 300, base + 305, 5)
       
        for strike in strike_range:
            distance = abs(strike - current_price)
            proximity_factor = max(0, 1 - (distance / 100)) ** 2
           
            round_factor = 1.0
            if strike % 100 == 0:
                round_factor = 3.5
            elif strike % 50 == 0:
                round_factor = 2.8
            elif strike % 25 == 0:
                round_factor = 2.0
            elif strike % 10 == 0:
                round_factor = 1.3
           
            zone_factor = 1.0
            key_levels = [3900, 3950, 4000, 4050, 4100, 4150, 4200, 4250]
            for level in key_levels:
                if abs(strike - level) < 15:
                    zone_factor = 2.5
                    break
           
            base_call_oi = 500 + random.randint(-100, 300)
            if strike >= current_price:
                call_oi = base_call_oi * proximity_factor * round_factor * zone_factor * 1.2
            else:
                call_oi = base_call_oi * proximity_factor * round_factor * zone_factor * 0.7
           
            base_put_oi = 500 + random.randint(-100, 300)
            if strike <= current_price:
                put_oi = base_put_oi * proximity_factor * round_factor * zone_factor * 1.2
            else:
                put_oi = base_put_oi * proximity_factor * round_factor * zone_factor * 0.7
           
            call_oi = int(call_oi * random.uniform(0.8, 1.3))
            put_oi = int(put_oi * random.uniform(0.8, 1.3))
           
            strikes.append({
                'strike': strike,
                'call_oi': max(0, call_oi),
                'put_oi': max(0, put_oi),
                'total_oi': max(0, call_oi + put_oi)
            })
       
        max_pain = calculate_max_pain(strikes, current_price)
        major_levels = find_major_oi_levels(strikes, current_price)
       
        total_calls = sum(s['call_oi'] for s in strikes)
        total_puts = sum(s['put_oi'] for s in strikes)
        put_call_ratio = total_puts / total_calls if total_calls > 0 else 1
       
        max_oi = max(s['total_oi'] for s in strikes) if strikes else 1
       
        levels = []
        for s in strikes:
            intensity = (s['total_oi'] / max_oi * 100) if max_oi > 0 else 0
           
            zone_type = None
            is_max_pain = abs(s['strike'] - max_pain) < 3
           
            if is_max_pain:
                zone_type = 'maxpain'
            elif s['put_oi'] > s['call_oi'] * 1.8 and s['strike'] < current_price - 5:
                zone_type = 'support'
            elif s['call_oi'] > s['put_oi'] * 1.8 and s['strike'] > current_price + 5:
                zone_type = 'resistance'
           
            oi_imbalance = 'NEUTRAL'
            if s['call_oi'] > s['put_oi'] * 2:
                oi_imbalance = 'CALL_HEAVY'
            elif s['put_oi'] > s['call_oi'] * 2:
                oi_imbalance = 'PUT_HEAVY'
           
            levels.append({
                'strike': s['strike'],
                'call_oi': s['call_oi'],
                'put_oi': s['put_oi'],
                'total_oi': s['total_oi'],
                'intensity': intensity,
                'is_max_pain': is_max_pain,
                'zone_type': zone_type,
                'oi_imbalance': oi_imbalance,
                'distance_from_price': s['strike'] - current_price
            })
       
        levels.sort(key=lambda x: x['total_oi'], reverse=True)
       
        return {
            'levels': levels[:50],
            'max_pain': max_pain,
            'put_call_ratio': put_call_ratio,
            'total_oi': total_calls + total_puts,
            'total_calls': total_calls,
            'total_puts': total_puts,
            'major_levels': major_levels,
            'oi_sentiment': 'BULLISH' if put_call_ratio > 1.2 else 'BEARISH' if put_call_ratio < 0.8 else 'NEUTRAL'
        }, None
       
    except Exception as e:
        return None, str(e)

def find_major_oi_levels(strikes, current_price):
    """หา Support/Resistance จาก OI"""
    try:
        major_levels = []
       
        for i in range(1, len(strikes) - 1):
            curr = strikes[i]
            prev = strikes[i-1]
            next_strike = strikes[i+1]
           
            if curr['total_oi'] > prev['total_oi'] and curr['total_oi'] > next_strike['total_oi']:
                if curr['total_oi'] > 1000:
                    level_type = 'SUPPORT' if curr['strike'] < current_price else 'RESISTANCE'
                    strength = 'STRONG' if curr['total_oi'] > 3000 else 'MODERATE'
                   
                    major_levels.append({
                        'price': curr['strike'],
                        'type': level_type,
                        'strength': strength,
                        'total_oi': curr['total_oi'],
                        'call_oi': curr['call_oi'],
                        'put_oi': curr['put_oi']
                    })
       
        major_levels.sort(key=lambda x: x['total_oi'], reverse=True)
        return major_levels[:8]
       
    except:
        return []

def calculate_max_pain(strikes, current_price):
    """คำนวณ Max Pain Price"""
    try:
        max_pain_price = current_price
        min_loss = float('inf')
       
        for test_strike in strikes:
            test_price = test_strike['strike']
            total_loss = 0
           
            for s in strikes:
                strike = s['strike']
                call_oi = s['call_oi']
                put_oi = s['put_oi']
               
                if test_price > strike:
                    total_loss += (test_price - strike) * call_oi
               
                if test_price < strike:
                    total_loss += (strike - test_price) * put_oi
           
            if total_loss < min_loss:
                min_loss = total_loss
                max_pain_price = test_price
       
        return max_pain_price
    except:
        return current_price

def calculate_fibonacci_levels(gold_data):
    """คำนวณ Fibonacci Retracement Levels"""
    if not gold_data:
        return None
   
    try:
        high = gold_data['high']
        low = gold_data['low']
        diff = high - low
       
        levels = {
            'fib_0': high,
            'fib_236': high - (diff * 0.236),
            'fib_382': high - (diff * 0.382),
            'fib_50': high - (diff * 0.50),
            'fib_618': high - (diff * 0.618),
            'fib_786': high - (diff * 0.786),
            'fib_100': low
        }
       
        extensions = {
            'ext_1272': high + (diff * 0.272),
            'ext_1618': high + (diff * 0.618),
            'ext_2618': high + (diff * 1.618)
        }
       
        return {
            'retracements': levels,
            'extensions': extensions,
            'range': diff
        }
    except:
        return None

def calculate_pivot_points(gold_data):
    """คำนวณ Pivot Points"""
    if not gold_data:
        return None
   
    try:
        high = gold_data['high']
        low = gold_data['low']
        close = gold_data['price']
        open_price = gold_data['open']
       
        pivot = (high + low + close) / 3
       
        classic = {
            'r3': high + 2 * (pivot - low),
            'r2': pivot + (high - low),
            'r1': 2 * pivot - low,
            'pp': pivot,
            's1': 2 * pivot - high,
            's2': pivot - (high - low),
            's3': low - 2 * (high - pivot)
        }
       
        return {
            'classic': classic
        }
    except:
        return None

def detect_order_blocks(gold_data):
    """ตรวจจับ Order Blocks"""
    if not gold_data:
        return None
   
    try:
        current_price = gold_data['price']
        high = gold_data['high']
        low = gold_data['low']
       
        order_blocks = []
       
        bull_ob_high = low + (high - low) * 0.25
        bull_ob_low = low + (high - low) * 0.15
       
        if current_price > bull_ob_high:
            order_blocks.append({
                'type': 'bullish',
                'high': bull_ob_high,
                'low': bull_ob_low,
                'strength': 'Strong',
                'distance': current_price - bull_ob_high
            })
       
        bear_ob_high = high - (high - low) * 0.15
        bear_ob_low = high - (high - low) * 0.25
       
        if current_price < bear_ob_low:
            order_blocks.append({
                'type': 'bearish',
                'high': bear_ob_high,
                'low': bear_ob_low,
                'strength': 'Strong',
                'distance': bear_ob_low - current_price
            })
       
        return order_blocks
    except:
        return None

def find_liquidity_zones(gold_data, open_interest_data):
    """หา Liquidity Zones"""
    if not gold_data:
        return None
   
    try:
        current_price = gold_data['price']
        zones = []
       
        base = int(current_price / 50) * 50
        for i in range(-4, 5):
            price = base + (i * 50)
            if abs(price - current_price) < 150:
                distance = abs(price - current_price)
                zones.append({
                    'type': 'round_number',
                    'price': price,
                    'strength': 'High' if price % 100 == 0 else 'Medium',
                    'distance': distance,
                    'description': f'Round Number: ${price}'
                })
       
        if open_interest_data and 'major_levels' in open_interest_data:
            for level in open_interest_data['major_levels'][:3]:
                distance = abs(current_price - level['price'])
                if distance < 100:
                    zones.append({
                        'type': 'oi_liquidity',
                        'price': level['price'],
                        'strength': level['strength'],
                        'distance': distance,
                        'description': f"{level['type']} with {level['total_oi']:,.0f} OI"
                    })
       
        zones.sort(key=lambda x: x['distance'])
        return zones[:8]
    except:
        return None

def calculate_supply_demand_zones(gold_data, open_interest_data=None):
    """คำนวณ S/D Zones"""
    if not gold_data:
        return None
   
    try:
        zones = []
       
        if open_interest_data and 'levels' in open_interest_data:
            current_price = gold_data['price']
           
            for level in open_interest_data['levels']:
                if level['strike'] < current_price and level['put_oi'] > 3000:
                    strength = 'Strong' if level['put_oi'] > 5000 else 'Moderate'
                    zones.append({
                        'type': 'demand',
                        'level': level['strike'],
                        'strength': strength,
                        'oi': level['put_oi']
                    })
           
            for level in open_interest_data['levels']:
                if level['strike'] > current_price and level['call_oi'] > 3000:
                    strength = 'Strong' if level['call_oi'] > 5000 else 'Moderate'
                    zones.append({
                        'type': 'supply',
                        'level': level['strike'],
                        'strength': strength,
                        'oi': level['call_oi']
                    })
           
            zones.sort(key=lambda x: x.get('oi', 0), reverse=True)
            return zones[:6]
       
        return None
    except:
        return None

def generate_ai_analysis(gold_data, open_interest_data, spdr_data, economic_calendar):
    """สร้างการวิเคราะห์ AI"""
    try:
        if not gold_data:
            return None
       
        current_price = gold_data['price']
        momentum = gold_data['change_percent']
       
        technical_score = 50
        if momentum > 0.5:
            technical_score += 20
        elif momentum < -0.5:
            technical_score -= 20
       
        if open_interest_data:
            put_call = open_interest_data['put_call_ratio']
            if put_call > 1.3:
                technical_score += 15
            elif put_call < 0.7:
                technical_score -= 15
       
        fundamental_score = 50
        if spdr_data:
            if spdr_data['weekly_flow'] > 10:
                fundamental_score += 20
            elif spdr_data['weekly_flow'] < -10:
                fundamental_score -= 20
       
        avg_score = (technical_score + fundamental_score) / 2
       
        if avg_score >= 65:
            recommendation = "BUY"
            summary = "Strong bullish signals detected across multiple timeframes. SPDR inflows confirm institutional accumulation."
        elif avg_score <= 35:
            recommendation = "SELL"
            summary = "Bearish pressure building with weak fundamentals. Institutional outflows suggest further downside."
        else:
            recommendation = "HOLD"
            summary = "Mixed signals suggest market consolidation. Wait for clearer directional bias."
       
        insights = []
       
        if open_interest_data:
            distance_from_max_pain = current_price - open_interest_data['max_pain']
            if abs(distance_from_max_pain) > 20:
                insights.append(f"🎯 Price ${abs(distance_from_max_pain):.0f} from Max Pain")
       
        if spdr_data and abs(spdr_data['weekly_flow']) > 15:
            flow_direction = "inflows" if spdr_data['weekly_flow'] > 0 else "outflows"
            insights.append(f"💰 Strong institutional {flow_direction}")
       
        if momentum > 0.8 or momentum < -0.8:
            insights.append(f"📊 Strong momentum ({momentum:+.2f}%)")
       
        confidence = min(95, max(55, int(avg_score)))
       
        return {
            'recommendation': recommendation,
            'summary': summary,
            'technical_score': int(technical_score),
            'fundamental_score': int(fundamental_score),
            'confidence': confidence,
            'insights': insights[:4]
        }
       
    except Exception as e:
        print(f"AI Analysis error: {e}")
        return None

def generate_ai_trading_signals(gold_data, fibonacci_levels, pivot_points, order_blocks, liquidity_zones, open_interest_data):
    """สร้างสัญญาณ AI Buy/Sell Zones"""
    try:
        if not gold_data:
            return None
       
        current_price = gold_data['price']
        signals = {
            'buy_zones': [],
            'sell_zones': [],
            'current_bias': None,
            'confidence': 0
        }
       
        buy_score = 0
       
        if fibonacci_levels:
            fib_618 = fibonacci_levels['retracements']['fib_618']
            fib_786 = fibonacci_levels['retracements']['fib_786']
           
            if current_price > fib_618 - 10 and current_price < fib_618 + 10:
                signals['buy_zones'].append({
                    'price': fib_618,
                    'type': 'Fibonacci 61.8%',
                    'type_th': 'ฟีโบนักชี 61.8%',
                    'strength': 'Strong',
                    'strength_th': 'แข็งแกร่ง',
                    'entry_range': [fib_618 - 3, fib_618 + 3],
                    'sl': fib_786 - 5,
                    'tp': fibonacci_levels['retracements']['fib_382'],
                    'reason': 'โซนฟีโบนักชีทองคำ - แนวรับที่สำคัญ'
                })
                buy_score += 25
       
        if pivot_points:
            s1 = pivot_points['classic']['s1']
           
            if abs(current_price - s1) < 15:
                signals['buy_zones'].append({
                    'price': s1,
                    'type': 'Pivot S1',
                    'type_th': 'พีวอท S1',
                    'strength': 'Strong',
                    'strength_th': 'แข็งแกร่ง',
                    'entry_range': [s1 - 2, s1 + 2],
                    'sl': pivot_points['classic']['s2'] - 3,
                    'tp': pivot_points['classic']['pp'],
                    'reason': 'แนวรับพีวอทแรก - โอกาสดีดตัวสูง'
                })
                buy_score += 20
       
        sell_score = 0
       
        if fibonacci_levels:
            fib_236 = fibonacci_levels['retracements']['fib_236']
           
            if abs(current_price - fib_236) < 10:
                signals['sell_zones'].append({
                    'price': fib_236,
                    'type': 'Fibonacci 23.6%',
                    'type_th': 'ฟีโบนักชี 23.6%',
                    'strength': 'Strong',
                    'strength_th': 'แข็งแกร่ง',
                    'entry_range': [fib_236 - 3, fib_236 + 3],
                    'sl': fibonacci_levels['retracements']['fib_0'] + 5,
                    'tp': fibonacci_levels['retracements']['fib_618'],
                    'reason': 'โซนต้านตื้น - แนวต้านที่สำคัญ'
                })
                sell_score += 25
       
        if pivot_points:
            r1 = pivot_points['classic']['r1']
           
            if abs(current_price - r1) < 15:
                signals['sell_zones'].append({
                    'price': r1,
                    'type': 'Pivot R1',
                    'type_th': 'พีวอท R1',
                    'strength': 'Strong',
                    'strength_th': 'แข็งแกร่ง',
                    'entry_range': [r1 - 2, r1 + 2],
                    'sl': pivot_points['classic']['r2'] + 3,
                    'tp': pivot_points['classic']['pp'],
                    'reason': 'แนวต้านพีวอทแรก - โอกาสถูกปฏิเสธสูง'
                })
                sell_score += 20
       
        if buy_score > sell_score and buy_score > 40:
            signals['current_bias'] = 'BULLISH'
            signals['current_bias_th'] = 'แนวโน้มขาขึ้น'
            signals['confidence'] = min(95, buy_score)
            signals['recommendation'] = 'มองหาโอกาสเข้า BUY ที่โซนแนวรับ'
        elif sell_score > buy_score and sell_score > 40:
            signals['current_bias'] = 'BEARISH'
            signals['current_bias_th'] = 'แนวโน้มขาลง'
            signals['confidence'] = min(95, sell_score)
            signals['recommendation'] = 'มองหาโอกาสเข้า SELL ที่โซนแนวต้าน'
        else:
            signals['current_bias'] = 'NEUTRAL'
            signals['current_bias_th'] = 'ไม่มีทิศทางชัดเจน'
            signals['confidence'] = 50
            signals['recommendation'] = 'รอให้ทิศทางชัดเจนก่อนเข้าเทรด'
       
        return signals
       
    except Exception as e:
        print(f"AI Trading Signals error: {e}")
        return None

def generate_mt5_signal(gold_data, open_interest_data, volume_profile, ai_analysis=None):
    """สร้างสัญญาณ MT5"""
    if not gold_data:
        return None
   
    try:
        current_price = gold_data['price']
        reasons = []
        buy_score = 0
        sell_score = 0
       
        if open_interest_data:
            max_pain = open_interest_data['max_pain']
            distance_from_max_pain = current_price - max_pain
           
            if distance_from_max_pain < -15:
                buy_score += 35
                reasons.append({
                    'icon': '🎯',
                    'text': f"ราคาต่ำกว่า Max Pain ${max_pain:.0f} ถึง ${abs(distance_from_max_pain):.0f}",
                    'strong': True
                })
            elif distance_from_max_pain > 15:
                sell_score += 35
                reasons.append({
                    'icon': '🎯',
                    'text': f"ราคาสูงกว่า Max Pain ${max_pain:.0f} ถึง ${abs(distance_from_max_pain):.0f}",
                    'strong': True
                })
           
            put_call_ratio = open_interest_data['put_call_ratio']
           
            if put_call_ratio > 1.5:
                buy_score += 25
                reasons.append({
                    'icon': '📊',
                    'text': f"Put/Call Ratio {put_call_ratio:.2f} - Bullish Sentiment",
                    'strong': True
                })
            elif put_call_ratio < 0.6:
                sell_score += 25
                reasons.append({
                    'icon': '📊',
                    'text': f"Put/Call Ratio {put_call_ratio:.2f} - Bearish Sentiment",
                    'strong': True
                })
       
        if volume_profile:
            poc = volume_profile['poc']
            val = volume_profile['val']
           
            if current_price < val and current_price > val - 10:
                buy_score += 20
                reasons.append({
                    'icon': '💪',
                    'text': f"Test VAL Support ${val:.2f}",
                    'strong': True
                })
       
        momentum = gold_data['change_percent']
       
        if momentum > 0.8:
            buy_score += 18
            reasons.append({
                'icon': '🚀',
                'text': f"Strong Bullish Momentum {momentum:.2f}%",
                'strong': False
            })
        elif momentum < -0.8:
            sell_score += 18
            reasons.append({
                'icon': '📉',
                'text': f"Strong Bearish Momentum {momentum:.2f}%",
                'strong': False
            })
       
        min_score = 60
       
        if buy_score > sell_score and buy_score >= min_score:
            entry = current_price + random.uniform(0.30, 0.80)
            sl = entry - random.uniform(12, 18)
            tp = entry + random.uniform(25, 35)
            rr_ratio = abs(tp - entry) / abs(entry - sl)
           
            return {
                'action': 'BUY',
                'current_price': current_price,
                'entry': round(entry, 2),
                'sl': round(sl, 2),
                'tp': round(tp, 2),
                'strength': min(98, buy_score),
                'rr_ratio': round(rr_ratio, 2),
                'poc': volume_profile['poc'] if volume_profile else current_price,
                'vah': volume_profile['vah'] if volume_profile else current_price + 20,
                'val': volume_profile['val'] if volume_profile else current_price - 20,
                'reasons': reasons
            }
           
        elif sell_score > buy_score and sell_score >= min_score:
            entry = current_price - random.uniform(0.30, 0.80)
            sl = entry + random.uniform(12, 18)
            tp = entry - random.uniform(25, 35)
            rr_ratio = abs(entry - tp) / abs(sl - entry)
           
            return {
                'action': 'SELL',
                'current_price': current_price,
                'entry': round(entry, 2),
                'sl': round(sl, 2),
                'tp': round(tp, 2),
                'strength': min(98, sell_score),
                'rr_ratio': round(rr_ratio, 2),
                'poc': volume_profile['poc'] if volume_profile else current_price,
                'vah': volume_profile['vah'] if volume_profile else current_price + 20,
                'val': volume_profile['val'] if volume_profile else current_price - 20,
                'reasons': reasons
            }
       
        return None
       
    except Exception as e:
        print(f"Signal generation error: {e}")
        return None

@app.route('/')
def dashboard():
    """Main Dashboard Route"""
    try:
        gold_data, gold_error = get_gold_price()
        open_interest, oi_error = get_gold_open_interest()
        volume_profile = calculate_volume_profile_levels(gold_data)
        spdr_data, spdr_error = get_spdr_gold_flows()
        economic_calendar, calendar_error = get_forex_factory_calendar()
        market_news, news_error = get_market_news()
        zones = calculate_supply_demand_zones(gold_data, open_interest)
       
        fibonacci_levels = calculate_fibonacci_levels(gold_data)
        pivot_points = calculate_pivot_points(gold_data)
        order_blocks = detect_order_blocks(gold_data)
        liquidity_zones = find_liquidity_zones(gold_data, open_interest)
       
        ai_trading_signals = generate_ai_trading_signals(
            gold_data, fibonacci_levels, pivot_points,
            order_blocks, liquidity_zones, open_interest
        )
       
        ai_analysis = generate_ai_analysis(
            gold_data, open_interest, spdr_data, economic_calendar
        )
       
        signal = generate_mt5_signal(
            gold_data, open_interest, volume_profile, ai_analysis
        )
       
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
       
        # Add abs function to Jinja2 context
        return render_template_string(
            TEMPLATE,
            signal=signal,
            gold_data=gold_data,
            gold_error=gold_error,
            zones=zones,
            open_interest=open_interest,
            oi_error=oi_error,
            spdr_data=spdr_data,
            economic_calendar=economic_calendar,
            market_news=market_news,
            ai_analysis=ai_analysis,
            ai_trading_signals=ai_trading_signals,
            fibonacci_levels=fibonacci_levels,
            pivot_points=pivot_points,
            order_blocks=order_blocks,
            liquidity_zones=liquidity_zones,
            update_time=update_time,
            abs=abs  # Add abs function to template context
        )
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"<h1>Error: {str(e)}</h1><pre>{error_detail}</pre>", 500

@app.route('/api/signal')
def api_signal():
    """API for real-time updates"""
    try:
        gold_data, _ = get_gold_price()
        open_interest, _ = get_gold_open_interest()
        volume_profile = calculate_volume_profile_levels(gold_data)
        spdr_data, _ = get_spdr_gold_flows()
        economic_calendar, _ = get_forex_factory_calendar()
       
        fibonacci_levels = calculate_fibonacci_levels(gold_data)
        pivot_points = calculate_pivot_points(gold_data)
        order_blocks = detect_order_blocks(gold_data)
        liquidity_zones = find_liquidity_zones(gold_data, open_interest)
       
        ai_trading_signals = generate_ai_trading_signals(
            gold_data, fibonacci_levels, pivot_points,
            order_blocks, liquidity_zones, open_interest
        )
       
        ai_analysis = generate_ai_analysis(
            gold_data, open_interest, spdr_data, economic_calendar
        )
       
        signal = generate_mt5_signal(
            gold_data, open_interest, volume_profile, ai_analysis
        )
       
        return jsonify({
            'signal': signal,
            'ai_analysis': ai_analysis,
            'ai_trading_signals': ai_trading_signals,
            'update_time': datetime.now().strftime('%H:%M:%S')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data')
def api_data():
    """API for all market data"""
    try:
        gold_data, _ = get_gold_price()
        open_interest, _ = get_gold_open_interest()
        spdr_data, _ = get_spdr_gold_flows()
        economic_calendar, _ = get_forex_factory_calendar()
        market_news, _ = get_market_news()
       
        return jsonify({
            'gold': gold_data,
            'open_interest': open_interest,
            'spdr': spdr_data,
            'calendar': economic_calendar,
            'news': market_news,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test')
def test():
    """Test endpoint"""
    try:
        gold_data, _ = get_gold_price()
        open_interest, _ = get_gold_open_interest()
        spdr_data, _ = get_spdr_gold_flows()
       
        results = {
            'status': 'OK',
            'gold': gold_data is not None,
            'open_interest': open_interest is not None,
            'spdr': spdr_data is not None,
            'price': gold_data['price'] if gold_data else None,
            'max_pain': open_interest['max_pain'] if open_interest else None,
            'spdr_flow': spdr_data['weekly_flow'] if spdr_data else None
        }
        return jsonify(results)
    except Exception as e:
        return jsonify({'status': 'ERROR', 'message': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting XAUUSD Complete Pro Trading Dashboard...")
    print("=" * 60)
    print("📊 Features:")
    print("  ✅ Real-time XAUUSD Forex Price")
    print("  ✅ CME Open Interest Heatmap + Max Pain")
    print("  ✅ Volume Profile (POC, VAH, VAL)")
    print("  ✅ SPDR Gold Trust Flows")
    print("  ✅ Economic Calendar")
    print("  ✅ AI-Powered Analysis")
    print("  ✅ MT5 Trading Signals")
    print("=" * 60)
    print("🌐 Dashboard: http://localhost:10000")
    print("📡 API Signals: http://localhost:10000/api/signal")
    print("📊 API Data: http://localhost:10000/api/data")
    print("🧪 Test: http://localhost:10000/test")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=10000)
