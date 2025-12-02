"""
HTML report generator with Plotly visualizations.

Generates interactive HTML reports comparing prompt performance across
languages and formality levels.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

from ..storage.cache_manager import CacheManager
from ..metrics import quantitative, qualitative
from ..constants import FORMALITY_LEVELS, SUPPORTED_LANGUAGES, REPORTS_DIR


class HTMLReportGenerator:
    """
    Generate interactive HTML reports with Plotly visualizations.

    Creates comprehensive reports comparing:
    - Token efficiency across languages
    - Cultural appropriateness scores
    - Lexical diversity metrics
    - Response length variations
    - Formality level adherence
    """

    def __init__(self, cache_manager: CacheManager):
        """
        Initialize report generator.

        Args:
            cache_manager: CacheManager instance for accessing cached data
        """
        self.cache = cache_manager

    def generate_prompt_report(
        self,
        prompt_id: str,
        output_path: Optional[Path] = None
    ) -> str:
        """
        Generate comprehensive HTML report for a single prompt across all variants.

        Args:
            prompt_id: Prompt template ID
            output_path: Output file path (default: reports/{prompt_id}_report.html)

        Returns:
            Path to generated HTML file
        """
        if output_path is None:
            output_path = REPORTS_DIR / f"{prompt_id}_report.html"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Collect data for all variants
        data = self._collect_variant_data(prompt_id)

        # Generate visualizations
        figs = []
        figs.append(self._create_token_comparison(data))
        figs.append(self._create_cultural_appropriateness_heatmap(data))
        figs.append(self._create_lexical_diversity_comparison(data))
        figs.append(self._create_length_distribution(data))
        figs.append(self._create_formality_radar(data))

        # Build HTML report
        html = self._build_html_report(prompt_id, data, figs)

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return str(output_path)

    def _collect_variant_data(self, prompt_id: str) -> List[Dict]:
        """Collect metrics data for all variants of a prompt."""
        # Use first 3 supported languages (en, de, es) - fr adapter not yet implemented
        languages = SUPPORTED_LANGUAGES[:3]

        data = []

        for lang in languages:
            for formality in FORMALITY_LEVELS:
                response = self.cache.get_cached_response(prompt_id, lang, formality)

                if response:
                    # Calculate metrics
                    quant_metrics = quantitative.calculate_all_quantitative_metrics(
                        response.content,
                        response.tokens_output,
                        lang
                    )

                    qual_metrics = qualitative.calculate_all_qualitative_metrics(
                        response.content,
                        lang,
                        formality,
                        'business'  # Default domain
                    )

                    # Extract cultural score - handle both numeric and string formats
                    cultural_rating = qual_metrics['cultural_appropriateness'].get('overall_rating', 3.0)
                    if isinstance(cultural_rating, str):
                        # Try to parse string ratings like "Good" → 4.0
                        rating_map = {'Excellent': 5.0, 'Good': 4.0, 'Adequate': 3.0, 'Fair': 2.0, 'Poor': 1.0}
                        cultural_score = rating_map.get(cultural_rating, 3.0)
                    else:
                        cultural_score = float(cultural_rating)

                    data.append({
                        'language': lang,
                        'formality': formality,
                        'tokens_in': response.tokens_input,
                        'tokens_out': response.tokens_output,
                        'word_count': quant_metrics['length_metrics']['word_count'],
                        'lexical_diversity': quant_metrics['lexical_diversity']['type_token_ratio'],
                        'cultural_score': cultural_score,
                        'content': response.content[:200] + '...' if len(response.content) > 200 else response.content
                    })

        return data

    def _create_token_comparison(self, data: List[Dict]) -> go.Figure:
        """Create grouped bar chart comparing token usage across variants."""
        fig = go.Figure()

        languages = sorted(set(d['language'] for d in data))

        for formality in FORMALITY_LEVELS:
            tokens_out = []
            for lang in languages:
                matching = [d for d in data if d['language'] == lang and d['formality'] == formality]
                tokens_out.append(matching[0]['tokens_out'] if matching else 0)

            fig.add_trace(go.Bar(
                name=formality.capitalize(),
                x=languages,
                y=tokens_out,
                text=tokens_out,
                textposition='auto'
            ))

        fig.update_layout(
            title='Token Output by Language and Formality',
            xaxis_title='Language',
            yaxis_title='Tokens',
            barmode='group',
            template='plotly_white',
            height=400
        )

        return fig

    def _create_cultural_appropriateness_heatmap(self, data: List[Dict]) -> go.Figure:
        """Create heatmap of cultural appropriateness scores."""
        languages = sorted(set(d['language'] for d in data))

        # Build matrix
        matrix = []
        for formality in FORMALITY_LEVELS:
            row = []
            for lang in languages:
                matching = [d for d in data if d['language'] == lang and d['formality'] == formality]
                row.append(matching[0]['cultural_score'] if matching else 0)
            matrix.append(row)

        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=languages,
            y=FORMALITY_LEVELS,
            colorscale='RdYlGn',
            text=matrix,
            texttemplate='%{text:.1f}',
            textfont={"size": 14},
            colorbar=dict(title="Score")
        ))

        fig.update_layout(
            title='Cultural Appropriateness Scores',
            xaxis_title='Language',
            yaxis_title='Formality Level',
            template='plotly_white',
            height=400
        )

        return fig

    def _create_lexical_diversity_comparison(self, data: List[Dict]) -> go.Figure:
        """Create scatter plot of lexical diversity."""
        fig = go.Figure()

        languages = sorted(set(d['language'] for d in data))

        for lang in languages:
            lang_data = [d for d in data if d['language'] == lang]

            fig.add_trace(go.Scatter(
                x=[d['formality'] for d in lang_data],
                y=[d['lexical_diversity'] for d in lang_data],
                mode='markers+lines',
                name=lang.upper(),
                marker=dict(size=12),
                line=dict(width=2)
            ))

        fig.update_layout(
            title='Lexical Diversity (Type-Token Ratio)',
            xaxis_title='Formality Level',
            yaxis_title='Type-Token Ratio',
            template='plotly_white',
            height=400,
            yaxis=dict(range=[0, 1])
        )

        return fig

    def _create_length_distribution(self, data: List[Dict]) -> go.Figure:
        """Create box plot of word count distribution."""
        fig = go.Figure()

        languages = sorted(set(d['language'] for d in data))

        for lang in languages:
            lang_data = [d for d in data if d['language'] == lang]
            word_counts = [d['word_count'] for d in lang_data]

            fig.add_trace(go.Box(
                y=word_counts,
                name=lang.upper(),
                boxmean='sd'
            ))

        fig.update_layout(
            title='Response Length Distribution by Language',
            yaxis_title='Word Count',
            template='plotly_white',
            height=400
        )

        return fig

    def _create_formality_radar(self, data: List[Dict]) -> go.Figure:
        """Create radar chart comparing metrics across formality levels."""
        fig = go.Figure()

        for formality in FORMALITY_LEVELS:
            formal_data = [d for d in data if d['formality'] == formality]

            if formal_data:
                avg_tokens = sum(d['tokens_out'] for d in formal_data) / len(formal_data)
                avg_words = sum(d['word_count'] for d in formal_data) / len(formal_data)
                avg_diversity = sum(d['lexical_diversity'] for d in formal_data) / len(formal_data)
                avg_cultural = sum(d['cultural_score'] for d in formal_data) / len(formal_data)

                fig.add_trace(go.Scatterpolar(
                    r=[avg_tokens / 100, avg_words / 50, avg_diversity * 100, avg_cultural * 20],
                    theta=['Tokens/100', 'Words/50', 'Diversity×100', 'Cultural×20'],
                    fill='toself',
                    name=formality.capitalize()
                ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            title='Average Metrics by Formality Level (Normalized)',
            template='plotly_white',
            height=500
        )

        return fig

    def _build_html_report(
        self,
        prompt_id: str,
        data: List[Dict],
        figures: List[go.Figure]
    ) -> str:
        """Build complete HTML report with visualizations and data tables."""

        # Convert figures to HTML
        fig_htmls = [fig.to_html(include_plotlyjs='cdn', div_id=f'plot_{i}')
                     for i, fig in enumerate(figures)]

        # Build data table
        table_rows = []
        for d in data:
            table_rows.append(f"""
                <tr>
                    <td>{d['language'].upper()}</td>
                    <td>{d['formality'].capitalize()}</td>
                    <td>{d['tokens_in']}</td>
                    <td>{d['tokens_out']}</td>
                    <td>{d['word_count']}</td>
                    <td>{d['lexical_diversity']:.3f}</td>
                    <td>{d['cultural_score']:.1f}/5.0</td>
                </tr>
            """)

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multilingual Prompt Report: {prompt_id}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .header p {{
            margin: 0;
            opacity: 0.9;
        }}
        .section {{
            background: white;
            padding: 30px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            margin-top: 0;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #667eea;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding: 20px;
        }}
        .metric-card {{
            display: inline-block;
            background: #f8f9fa;
            padding: 20px;
            margin: 10px;
            border-radius: 8px;
            min-width: 150px;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        .metric-label {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌍 Multilingual Prompt Optimization Report</h1>
        <p><strong>Prompt ID:</strong> {prompt_id}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Variants Analyzed:</strong> {len(data)}</p>
    </div>

    <div class="section">
        <h2>📊 Summary Metrics</h2>
        <div class="metric-card">
            <div class="metric-value">{len(set(d['language'] for d in data))}</div>
            <div class="metric-label">Languages</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{len(set(d['formality'] for d in data))}</div>
            <div class="metric-label">Formality Levels</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{sum(d['tokens_out'] for d in data)}</div>
            <div class="metric-label">Total Tokens</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{sum(d['word_count'] for d in data)}</div>
            <div class="metric-label">Total Words</div>
        </div>
    </div>

    <div class="section">
        <h2>📈 Token Usage Analysis</h2>
        {fig_htmls[0]}
    </div>

    <div class="section">
        <h2>🎯 Cultural Appropriateness</h2>
        {fig_htmls[1]}
    </div>

    <div class="section">
        <h2>📚 Lexical Diversity</h2>
        {fig_htmls[2]}
    </div>

    <div class="section">
        <h2>📏 Response Length Distribution</h2>
        {fig_htmls[3]}
    </div>

    <div class="section">
        <h2>🎭 Formality Comparison</h2>
        {fig_htmls[4]}
    </div>

    <div class="section">
        <h2>📋 Detailed Data Table</h2>
        <table>
            <thead>
                <tr>
                    <th>Language</th>
                    <th>Formality</th>
                    <th>Tokens In</th>
                    <th>Tokens Out</th>
                    <th>Words</th>
                    <th>Lexical Diversity</th>
                    <th>Cultural Score</th>
                </tr>
            </thead>
            <tbody>
                {''.join(table_rows)}
            </tbody>
        </table>
    </div>

    <div class="footer">
        <p>Generated with <strong>Multilingual Prompt Optimizer</strong></p>
        <p>Powered by Gemma 2 9B (LMStudio) • Plotly Visualizations</p>
    </div>
</body>
</html>
"""
        return html
