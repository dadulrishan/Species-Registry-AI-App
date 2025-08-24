import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "./components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "./components/ui/dialog";
import { Badge } from "./components/ui/badge";
import { Trash2, Edit2, Plus, Search } from "lucide-react";
import { useToast } from "./hooks/use-toast";
import { Toaster } from "./components/ui/toaster";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SPECIES_OPTIONS = ['capuchin', 'macaque', 'marmoset', 'howler'];

const MonkeyForm = ({ monkey, onSave, onCancel, isEdit = false }) => {
  const [formData, setFormData] = useState({
    name: monkey?.name || '',
    species: monkey?.species || '',
    age_years: monkey?.age_years || '',
    favourite_fruit: monkey?.favourite_fruit || '',
    last_checkup_at: monkey?.last_checkup_at || ''
  });
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        ...formData,
        age_years: parseInt(formData.age_years) || 0
      };

      if (isEdit) {
        await axios.put(`${API}/monkeys/${monkey.monkey_id}`, payload);
        toast({
          title: "Success",
          description: "Monkey updated successfully!"
        });
      } else {
        await axios.post(`${API}/monkeys`, payload);
        toast({
          title: "Success", 
          description: "Monkey created successfully!"
        });
      }
      onSave();
    } catch (error) {
      console.error('Error submitting form:', error);
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          "Something went wrong!";
      toast({
        variant: "destructive",
        title: "Error",
        description: typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage)
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="name">Name *</Label>
        <Input
          id="name"
          value={formData.name}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          placeholder="Enter monkey name (2-40 characters)"
          required
          minLength={2}
          maxLength={40}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="species">Species *</Label>
        <Select value={formData.species} onValueChange={(value) => setFormData({...formData, species: value})}>
          <SelectTrigger>
            <SelectValue placeholder="Select species" />
          </SelectTrigger>
          <SelectContent>
            {SPECIES_OPTIONS.map(species => (
              <SelectItem key={species} value={species}>
                {species.charAt(0).toUpperCase() + species.slice(1)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label htmlFor="age">Age (years) *</Label>
        <Input
          id="age"
          type="number"
          value={formData.age_years}
          onChange={(e) => setFormData({...formData, age_years: e.target.value})}
          placeholder="0-45 years (marmosets max 22)"
          required
          min={0}
          max={45}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="fruit">Favourite Fruit *</Label>
        <Input
          id="fruit"
          value={formData.favourite_fruit}
          onChange={(e) => setFormData({...formData, favourite_fruit: e.target.value})}
          placeholder="Enter favourite fruit"
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="checkup">Last Checkup Date</Label>
        <Input
          id="checkup"
          type="datetime-local"
          value={formData.last_checkup_at}
          onChange={(e) => setFormData({...formData, last_checkup_at: e.target.value})}
        />
      </div>

      <DialogFooter>
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? 'Saving...' : (isEdit ? 'Update' : 'Create')} Monkey
        </Button>
      </DialogFooter>
    </form>
  );
};

const MonkeyCard = ({ monkey, onEdit, onDelete }) => {
  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString();
  };

  const getSpeciesColor = (species) => {
    const colors = {
      capuchin: 'bg-blue-100 text-blue-800',
      macaque: 'bg-green-100 text-green-800', 
      marmoset: 'bg-purple-100 text-purple-800',
      howler: 'bg-orange-100 text-orange-800'
    };
    return colors[species] || 'bg-gray-100 text-gray-800';
  };

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-lg">{monkey.name}</CardTitle>
            <CardDescription>ID: {monkey.monkey_id.slice(0, 8)}...</CardDescription>
          </div>
          <Badge className={getSpeciesColor(monkey.species)}>
            {monkey.species.charAt(0).toUpperCase() + monkey.species.slice(1)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="text-sm">
          <span className="font-medium">Age:</span> {monkey.age_years} years
        </div>
        <div className="text-sm">
          <span className="font-medium">Favourite Fruit:</span> {monkey.favourite_fruit}
        </div>
        <div className="text-sm">
          <span className="font-medium">Last Checkup:</span> {formatDate(monkey.last_checkup_at)}
        </div>
      </CardContent>
      <CardFooter className="pt-2">
        <div className="flex space-x-2 w-full">
          <Button variant="outline" size="sm" onClick={() => onEdit(monkey)} className="flex-1">
            <Edit2 className="w-4 h-4 mr-1" />
            Edit
          </Button>
          <Button variant="destructive" size="sm" onClick={() => onDelete(monkey.monkey_id)} className="flex-1">
            <Trash2 className="w-4 h-4 mr-1" />
            Delete
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
};

function App() {
  const [monkeys, setMonkeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [speciesFilter, setSpeciesFilter] = useState('');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingMonkey, setEditingMonkey] = useState(null);
  const { toast } = useToast();

  const fetchMonkeys = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (speciesFilter && speciesFilter !== 'all') params.append('species', speciesFilter);
      if (searchTerm) params.append('search', searchTerm);
      
      const response = await axios.get(`${API}/monkeys?${params}`);
      setMonkeys(response.data);
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to fetch monkeys"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (monkeyId) => {
    if (!window.confirm('Are you sure you want to delete this monkey?')) return;
    
    try {
      await axios.delete(`${API}/monkeys/${monkeyId}`);
      toast({
        title: "Success",
        description: "Monkey deleted successfully!"
      });
      fetchMonkeys();
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error", 
        description: "Failed to delete monkey"
      });
    }
  };

  const handleFormSave = () => {
    setIsCreateDialogOpen(false);
    setEditingMonkey(null);
    fetchMonkeys();
  };

  const handleCreateDialogClose = (open) => {
    setIsCreateDialogOpen(open);
    // Reset form when dialog closes
    if (!open) {
      // Force form reset by unmounting and remounting
      setTimeout(() => {
        setIsCreateDialogOpen(false);
      }, 100);
    }
  };

  useEffect(() => {
    fetchMonkeys();
  }, [searchTerm, speciesFilter]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">🐒 Monkey Registry</h1>
          <p className="text-gray-600">Manage your primate companions with ease</p>
        </div>

        {/* Controls */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="Search by name or species..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={speciesFilter} onValueChange={setSpeciesFilter}>
            <SelectTrigger className="w-full md:w-48">
              <SelectValue placeholder="Filter by species" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Species</SelectItem>
              {SPECIES_OPTIONS.map(species => (
                <SelectItem key={species} value={species}>
                  {species.charAt(0).toUpperCase() + species.slice(1)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Dialog open={isCreateDialogOpen} onOpenChange={handleCreateDialogClose}>
            <DialogTrigger asChild>
              <Button className="w-full md:w-auto">
                <Plus className="w-4 h-4 mr-2" />
                Add Monkey
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Add New Monkey</DialogTitle>
                <DialogDescription>
                  Create a new monkey registry entry
                </DialogDescription>
              </DialogHeader>
              <MonkeyForm
                onSave={handleFormSave}
                onCancel={() => setIsCreateDialogOpen(false)}
              />
            </DialogContent>
          </Dialog>
        </div>

        {/* Loading State */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-amber-600"></div>
            <p className="mt-2 text-gray-600">Loading monkeys...</p>
          </div>
        ) : (
          <>
            {/* Stats */}
            <div className="mb-6 text-center text-gray-600">
              <p>Total monkeys: {monkeys.length}</p>
            </div>

            {/* Monkey Grid */}
            {monkeys.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🐒</div>
                <h3 className="text-xl font-semibold text-gray-700 mb-2">No monkeys found</h3>
                <p className="text-gray-600 mb-4">
                  {searchTerm || speciesFilter ? 'Try adjusting your search criteria' : 'Start by adding your first monkey!'}
                </p>
                {!searchTerm && !speciesFilter && (
                  <Button onClick={() => setIsCreateDialogOpen(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Your First Monkey
                  </Button>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {monkeys.map((monkey) => (
                  <MonkeyCard
                    key={monkey.monkey_id}
                    monkey={monkey}
                    onEdit={setEditingMonkey}
                    onDelete={handleDelete}
                  />
                ))}
              </div>
            )}
          </>
        )}

        {/* Edit Dialog */}
        <Dialog open={!!editingMonkey} onOpenChange={() => setEditingMonkey(null)}>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Edit Monkey</DialogTitle>
              <DialogDescription>
                Update monkey information
              </DialogDescription>
            </DialogHeader>
            {editingMonkey && (
              <MonkeyForm
                monkey={editingMonkey}
                isEdit={true}
                onSave={handleFormSave}
                onCancel={() => setEditingMonkey(null)}
              />
            )}
          </DialogContent>
        </Dialog>

        <Toaster />
      </div>
    </div>
  );
}

export default App;