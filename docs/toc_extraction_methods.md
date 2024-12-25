# TOC Extraction Methods

## Available Methods

### 1. NCX-based Extraction
- Uses existing NCX file if present
- Most reliable when available
- Preserves original structure
- Limited by NCX quality

### 2. OPF-based Extraction
- Uses spine and manifest
- Creates basic linear structure
- Good for simple books
- Misses internal sections

### 3. Content Analysis
- Analyzes actual content
- Finds natural divisions
- More complex but flexible
- Better for complex books

### 4. Hybrid Approach
- Combines multiple methods
- Falls back gracefully
- Best overall results
- More processing overhead

## Method Selection

### Decision Factors
1. EPUB version
2. Available metadata
3. Content structure
4. Required detail level
5. Performance needs

### Selection Matrix
```
Priority | NCX Present | Structure | Method
---------|-------------|-----------|--------
1        | Yes        | Any       | NCX
2        | No         | Simple    | OPF
3        | No         | Complex   | Content
4        | No         | Unknown   | Hybrid
```

## Implementation Details

### NCX Method
```python
def extract_from_ncx(ncx_path):
    """
    Extract TOC from NCX file
    """
    toc = []
    # Parse NCX
    # Extract navMap
    # Build TOC structure
    return toc
```

### OPF Method
```python
def extract_from_opf(opf_path):
    """
    Extract TOC from OPF file
    """
    toc = []
    # Parse OPF
    # Process spine
    # Map to manifest
    return toc
```

### Content Analysis Method
```python
def analyze_content(content):
    """
    Extract TOC from content analysis
    """
    toc = []
    # Find structure markers
    # Identify sections
    # Build hierarchy
    return toc
```

### Hybrid Method
```python
def hybrid_extraction(epub_path):
    """
    Combined extraction approach
    """
    toc = None
    # Try NCX
    if has_ncx():
        toc = extract_from_ncx()
    # Try OPF
    if not toc and has_opf():
        toc = extract_from_opf()
    # Fall back to content
    if not toc:
        toc = analyze_content()
    return toc
```

## Content Analysis Patterns

### Text Markers
1. Numeric patterns
   - "Chapter 1", "Part I"
   - "Section 1.2"
   - Numbered lists

2. Semantic markers
   - "Introduction"
   - "Conclusion"
   - "Appendix"

3. Visual separators
   - "***"
   - "---"
   - Blank lines

### HTML Structure
1. Heading elements
   - `<h1>` through `<h6>`
   - Nested structure
   - Heading classes

2. Semantic elements
   - `<section>`
   - `<article>`
   - `<nav>`

3. Custom markup
   - Class names
   - ID patterns
   - Data attributes

## Processing Steps

### 1. Pre-processing
```python
def preprocess_content(content):
    """
    Prepare content for analysis
    """
    # Clean markup
    # Normalize structure
    # Identify patterns
```

### 2. Structure Analysis
```python
def analyze_structure(content):
    """
    Identify content structure
    """
    # Find divisions
    # Extract hierarchy
    # Map relationships
```

### 3. TOC Generation
```python
def generate_toc(structure):
    """
    Generate TOC from structure
    """
    # Build TOC tree
    # Add metadata
    # Create navigation
```

## Quality Assurance

### Validation
1. Structure integrity
2. Link validation
3. Hierarchy check
4. Metadata consistency

### Testing
1. Unit tests
2. Integration tests
3. Edge cases
4. Performance tests

## Performance Optimization

### Caching
1. Pattern cache
2. Structure cache
3. Result cache

### Processing
1. Lazy loading
2. Parallel processing
3. Early termination

## Error Handling

### Common Issues
1. Missing files
2. Invalid structure
3. Broken links
4. Encoding issues

### Recovery
1. Fallback methods
2. Default structure
3. Error logging
4. User notification

## Usage Guidelines

### Best Practices
1. Try NCX first
2. Fall back to OPF
3. Use content analysis as last resort
4. Combine methods when needed

### Configuration
1. Method selection
2. Pattern definitions
3. Performance settings
4. Output format

## Maintenance

### Updates
1. Pattern database
2. Method priorities
3. Performance tuning
4. Bug fixes

### Monitoring
1. Success rates
2. Error patterns
3. Performance metrics
4. Usage statistics 