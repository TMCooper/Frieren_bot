const express = require('express');
const ListCalculator = require('./Calc/Calculate.js');

function register(app) {
  app.use(express.json());

  app.get('/api/CalculatePrice', (req, res) => {
    const tool = req.query;

    const requiredParams = ['Name', 'Weight'];

    for (const param of requiredParams) {
      if (!tool || !tool[param]) {
        return res.status(400).json({ error: `Missing required parameter: ${param}` });
      }
    }

    try {
      tool.Weight = { value: parseFloat(tool.Weight) };

      tool.Variant = { value: tool.Variant || 'Normal' };

      if (tool.Mutation) {
        tool.attributes = tool.Mutation.split(',').map(m => m.trim());
      } else {
        tool.attributes = [];
      }

      const result = ListCalculator.calculateFruit(tool);
      return res.json({ value: result });
    } catch (error) {
      console.error("Error calculating fruit value:", error);
      return res.status(500).json({ error: "Internal server error" });
    }
  });
}

module.exports = { register };
